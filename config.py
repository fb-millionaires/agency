import os

basedir = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'


class Config(object):
    SECRET_KEY = 'that_uyona_boy_wanna_do_good'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir, 'agency.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_TOKEN_AUTH = True
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100


class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://your_db_user:password@localhost:3306/database'
    DEBUG = True
