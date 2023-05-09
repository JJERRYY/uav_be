import logging
import os

from sqlalchemy.orm import joinedload

from main.models import *
from . import create_app
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_caching import Cache

import config

# db = SQLAlchemy()
#
# app = Flask(__name__)
# app.config.from_object(config.Config)
# with app.app_context():
#     db.init_app(app)
#     db.create_all()
#
app, cache = create_app()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/trainingdata/list', methods=['GET'])
@cache.cached(timeout=0)
def get_training_data_list():
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)
    total_count = TrainingData.query.count()
    if page is not None and per_page is not None:
        # 如果 page 和 per_page 参数都存在，则返回分页的列表
        training_data_list = TrainingData.query.order_by(TrainingData.training_data_datetime.desc()).paginate(page=page,
                                                                                                              per_page=per_page,
                                                                                                              error_out=False).items
        # training_data_list = TrainingData.query.options(
        #     joinedload(TrainingData.episodes).joinedload(Episode.steps)
        # ).order_by(TrainingData.training_data_datetime.desc()).paginate(page=page, per_page=per_page,
        #                                                                 error_out=False).items
    else:
        # 否则，返回所有列表
        training_data_list = TrainingData.query.order_by(TrainingData.training_data_datetime.desc()).all()
        # training_data_list = TrainingData.query.options(
        #     joinedload(TrainingData.episodes).joinedload(Episode.steps)
        # ).order_by(TrainingData.training_data_datetime.desc()).all()

    result = []
    for training_data in training_data_list:
        config = {
            'actor_lr': training_data.config.actor_lr,
            'critic_lr': training_data.config.critic_lr,
            'num_episodes': training_data.config.num_episodes,
            'num_steps': training_data.config.num_steps,
            'gamma': training_data.config.gamma,
            'hidden_dim': training_data.config.hidden_dim,
            'tau': training_data.config.tau,
            'buffer_size': training_data.config.buffer_size,
            'minimal_size': training_data.config.minimal_size,
            'batch_size': training_data.config.batch_size,
            'sigma': training_data.config.sigma,
            'num_uavs': training_data.config.num_uavs,
            'num_users': training_data.config.num_users,
            'env_name': training_data.config.env_name,
            'time_consumpted': training_data.config.time_consumpted,
            'alg': training_data.config.alg,
            'info': training_data.config.info,
        }

        episodes = []
        for episode in training_data.episodes:
            steps = []
            for step in episode.steps:
                state = {
                    'uav_position': step.state.uav_position,
                    'user_position': step.state.user_position,
                    'user_rate': step.state.user_rate
                }
                action = {
                    # 'uav_direction_distance': step.action.uav_direction_distance,
                    'uav_power': step.action.uav_power,
                    'uav_association': step.action.uav_association
                }
                next_state = {
                    'uav_position': step.next_state.uav_position,
                    'user_position': step.next_state.user_position,
                    'user_rate': step.next_state.user_rate
                }
                steps.append({
                    'id': step.id,
                    'state': state,
                    'action': action,
                    'reward': step.reward,
                    # 'next_state': next_state,
                    'done': step.done
                })
            episodes.append({
                'episode_id': episode.episode_id,
                'step_data': steps,
                'num_step': episode.num_step,
                'total_reward': episode.total_reward,
                'actor_loss': episode.actor_loss,
                'critic_loss': episode.critic_loss,
            })

        result.append({
            "id": training_data.id,
            "data": episodes,
            "config": config,
            "datetime": training_data.training_data_datetime,
            'returns_list': training_data.returns_list,
            'loss_list': training_data.loss_list
        })

    return jsonify({"total_count": total_count, "data": result})


@app.route('/trainingdata/<int:id>', methods=['GET'])
def get_training_data(id):
    training_data = TrainingData.query.get(id)
    if training_data is None:
        return jsonify({'error': 'Training data not found'}), 404

    config = {
        'actor_lr': training_data.config.actor_lr,
        'critic_lr': training_data.config.critic_lr,
        'num_episodes': training_data.config.num_episodes,
        'num_steps': training_data.config.num_steps,
        'gamma': training_data.config.gamma,
        'hidden_dim': training_data.config.hidden_dim,
        'tau': training_data.config.tau,
        'buffer_size': training_data.config.buffer_size,
        'minimal_size': training_data.config.minimal_size,
        'batch_size': training_data.config.batch_size,
        'sigma': training_data.config.sigma,
        'num_uavs': training_data.config.num_uavs,
        'num_users': training_data.config.num_users,
        'env_name': training_data.config.env_name,
        'info': training_data.config.info,
        'alg': training_data.config.alg,
        'time_consumpted': training_data.config.time_consumpted,
    }

    episodes = []
    for episode in training_data.episodes:
        steps = []
        for step in episode.steps:
            state = {
                'uav_position': step.state.uav_position,
                'user_position': step.state.user_position,
                'user_rate': step.state.user_rate
            }
            action = {
                'uav_direction_distance': step.action.uav_direction_distance,
                'uav_power': step.action.uav_power,
                'uav_association': step.action.uav_association
            }
            next_state = {
                'uav_position': step.next_state.uav_position,
                'user_position': step.next_state.user_position,
                'user_rate': step.next_state.user_rate
            }
            steps.append({
                'id': step.id,
                'state': state,
                'action': action,
                'reward': step.reward,
                'next_state': next_state,
                'done': step.done
            })
        episodes.append({
            'episode_id': episode.episode_id,
            'step_data': steps,
            'num_step': episode.num_step,
            'total_reward': episode.total_reward
        })

    result = {
        'code': 0,
        'data': {
            'id': training_data.id,
            'episodes': episodes,
            'config': config,
            'datetime': training_data.training_data_datetime,
            # 'last_avg_return': 'string',
            'returns_list': training_data.returns_list,
            'loss_list': training_data.loss_list
        }
    }

    return jsonify(result)


@app.route('/delete_training_data', methods=['GET'])
def delete_training_data():
    cache.clear()
    id = request.args.get('id')
    if id is not None:
        training_data = TrainingData.query.get(id)
        if training_data is not None:
            db.session.delete(training_data)
            db.session.commit()
            cache.clear()
            return 'Training data deleted',200
        else:
            return 'Training data not found'
    else:
        return 'Missing id parameter'


@app.route('/trainingdata', methods=['POST'])
def put_trainingdata():
    data = request.get_json()
    # logging.log(data)
    training_data = TrainingData(
        # id=data['id'],
        training_data_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        returns_list=data['returns_list'],
        loss_list=data['loss_list'],
    )


    config = Config(
        actor_lr=data['config']['actor_lr'],
        critic_lr=data['config']['critic_lr'],
        num_episodes=data['config']['num_episodes'],
        num_steps=data['config']['num_steps'],
        gamma=data['config']['gamma'],
        hidden_dim=data['config']['hidden_dim'],
        tau=data['config']['tau'],
        buffer_size=data['config']['buffer_size'],
        minimal_size=data['config']['minimal_size'],
        batch_size=data['config']['batch_size'],
        sigma=data['config']['sigma'],
        num_uavs=data['config']['num_uavs'],
        num_users=data['config']['num_users'],
        env_name=data['config']['env_name'],
        alg = data['config']['alg'],
        time_consumpted=data['config']['time_consumpted'],
        info=data['config']['info'],
    )
    training_data.config = config
    for episode_data in data['data']:
        total_reward = 0
        episode = Episode(
            episode_id=episode_data['episode_id'],
            num_step=episode_data['num_step'],
            # total_reward=episode_data['total_reward']
        )
        for step_data in episode_data['step_data']:
            # state = State(
            #     uav_position=step_data['state']['uav_position'],
            #     user_position=step_data['state']['user_position'],
            #     user_rate=step_data['state']['user_rate']
            # )
            # action = Action(
            #     uav_direction_distance=step_data['action']['uav_direction_distance'],
            #     uav_power=step_data['action']['uav_power'],
            #     uav_association=step_data['action']['uav_association']
            # )
            # next_state = State(
            #     uav_position=step_data['next_state']['uav_position'],
            #     user_position=step_data['next_state']['user_position'],
            #     user_rate=step_data['next_state']['user_rate']
            # )
            # state = State(
            #     uav_position=step_data['state'].get('uav_position', []),
            #     user_position=step_data['state'].get('user_position', []),
            #     user_rate=step_data['state'].get('user_rate', [])
            # )
            if step_data['state'] is None:
                state = State(
                    uav_position=[],
                    user_position=[],
                    user_rate=[]
                )
            else:
                state = State(
                    uav_position=step_data['state'].get('uav_position', []),
                    user_position=step_data['state'].get('user_position', []),
                    user_rate=step_data['state'].get('user_rate', [])
                )
            if step_data['action'] is None:
                action = Action(
                    uav_direction_distance=[],
                    uav_power=[],
                    uav_association=[]
                )
            else:
                action = Action(
                    uav_direction_distance=step_data['action'].get('uav_direction_distance', []),
                    uav_power=step_data['action'].get('uav_power', []),
                    uav_association=step_data['action'].get('uav_association', [])
                )
            if step_data['next_state'] is None:
                next_state = State(
                    uav_position=[],
                    user_position=[],
                    user_rate=[])
            else:
                next_state = State(
                    uav_position=step_data['next_state'].get('uav_position', []),
                    user_position=step_data['next_state'].get('user_position', []),
                    user_rate=step_data['next_state'].get('user_rate', []))

            step = Step(
                id=step_data['id'],
                done=step_data['done'],
                reward=step_data['reward']
            )
            total_reward += step.reward
            step.state = state
            step.action = action
            step.next_state = next_state
            episode.steps.append(step)
        episode.total_reward = total_reward
        training_data.episodes.append(episode)
    db.session.add(training_data)
    db.session.commit()
    cache.clear()
    return 'success', 200


#
# @app.route('/trainningdata/list', methods=['GET'])
# def get_training_data_list():
#     training_data = ['data1', 'data2', 'data3']  # 假设这是训练数据列表
#     return jsonify(training_data)
#
# @app.route('/trainningdata/<int:id>', methods=['GET'])
# def get_trainningdata(id):
#     # 根据ID获取训练数据
#     return 'Trainning Data ID: %d' % id

if __name__ == '__main__':
    # app.run(host="192.168.0.112", port=5000)
    app.run()
