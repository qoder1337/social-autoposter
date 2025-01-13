import os
from dotenv import load_dotenv
from pytz import timezone

# Berlin-Zeitzone definieren
BERLIN_TZ = timezone("Europe/Berlin")

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, ".env"))


class Config(object):
    DATABASE_CONNECT_OPTIONS = {}

    # Turn off Flask-SQLAlchemy event system
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASEDIR, "database", "tweet_posts.db"
    )


class DevelopmentConfig(Config):
    """Statement for enabling the development environment"""

    # Define the database - we are working with
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASEDIR, "database", "dev_xposts.db"
    )
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASEDIR, "database", "test_posts.db"
    )


set_config = {
    "base": Config,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
