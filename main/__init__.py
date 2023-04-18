"""Initialize Flask app."""

from flask import Flask
from flask_caching import Cache
from flask_compress import Compress
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS

import config
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
# db = SQLAlchemy()
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))



def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    CORS(app)
    Compress(app)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    app.config.from_object(config.Config)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )


    db.init_app(app)
    migrate = Migrate(app, db,render_as_batch=True)

    with app.app_context():
        from main import models
        db.create_all()  # Create database tables for our data models

        return app,cache
