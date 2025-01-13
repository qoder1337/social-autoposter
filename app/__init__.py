from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import set_config


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name):
    """
    dynamic environment via config_name
    """
    app = Flask(__name__)

    app.config.from_object(set_config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    return app
