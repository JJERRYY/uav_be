# from app import db
from . import db
from datetime import datetime
from sqlalchemy import Column, Integer, JSON, String
from flask_sqlalchemy import SQLAlchemy


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer, primary_key=True)
    actor_lr = db.Column(db.Float)
    batch_size = db.Column(db.Float)
    buffer_size = db.Column(db.Float)
    critic_lr = db.Column(db.Float)
    env_name = db.Column(db.String)
    gamma = db.Column(db.Float)
    hidden_dim = db.Column(db.Integer)
    minimal_size = db.Column(db.Float)
    num_episodes = db.Column(db.Integer)
    num_steps = db.Column(db.Integer)
    num_uavs = db.Column(db.Integer)
    num_users = db.Column(db.Integer)
    sigma = db.Column(db.Float)
    tau = db.Column(db.Float)
    time_consumpted = db.Column(db.String)
    alg = db.Column(db.String)
    info = db.Column(db.String)

    def __repr__(self):
        return f"<Config(id={self.id}, actor_lr={self.actor_lr}, batch_size={self.batch_size}, buffer_size={self.buffer_size}, critic_lr={self.critic_lr}, env_name='{self.env_name}', gamma={self.gamma}, hidden_dim={self.hidden_dim}, minimal_size={self.minimal_size}, num_episodes={self.num_episodes}, num_steps={self.num_steps}, num_uavs={self.num_uavs}, num_users={self.num_users}, sigma={self.sigma}, tau={self.tau})>"


class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    uav_association = db.Column(db.PickleType)
    uav_direction_distance = db.Column(db.PickleType)
    uav_power = db.Column(db.PickleType)


class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    uav_position = db.Column(db.PickleType)
    user_position = db.Column(db.PickleType)
    user_rate = db.Column(db.PickleType)


class Step(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.Integer, db.ForeignKey('action.id'))
    action = db.relationship('Action', backref='steps', single_parent=True, cascade="all, delete-orphan")
    done = db.Column(db.Boolean)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State', foreign_keys=[state_id], backref='steps', single_parent=True,
                            cascade="all, delete-orphan")
    next_state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    # next_state = db.relationship('State', foreign_keys=[next_state_id],backref='steps')
    next_state = db.relationship('State', foreign_keys=[next_state_id], single_parent=True,
                                 cascade="all, delete-orphan")

    episode_id = db.Column(db.String(50), db.ForeignKey('episode.episode_id'))
    reward = db.Column(db.Float)


class Episode(db.Model):
    """episode"""
    __tablename__ = 'episode'
    episode_id = db.Column(db.Integer, primary_key=True)
    num_step = db.Column(db.Integer)
    total_reward = db.Column(db.Float)
    steps = db.relationship('Step', backref='episode', lazy='dynamic', cascade="all, delete-orphan")
    training_data_id = db.Column(db.Integer, db.ForeignKey('trainning_data.id'))

    actor_loss = db.Column(db.Float)
    critic_loss =  db.Column(db.Float)


class TrainingData(db.Model):
    """trainningData"""
    __tablename__ = 'trainning_data'
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('config.id'))
    training_data_datetime = db.Column(db.String(50))
    config = db.relationship('Config', backref='training_data', single_parent=True, cascade="all, delete-orphan")
    # episodes = db.relationship('Episode', backref='training_data', lazy='dynamic')
    episodes = db.relationship('Episode', backref='training_data', lazy='dynamic', cascade="all, delete-orphan")
