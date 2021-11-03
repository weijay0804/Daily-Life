'''

    daily life app 系統環境變數
    
    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/26
    update by : jay

'''

import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DAILY_LIFE_ADMIN = os.environ.get('DAILY_LIFE_ADMIN')
    POSTS_PER_PAGE = 10

    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ProductionConfig(Config):
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_REDIRECT = True if os.environ.get('DYNO') else False


config = {
    'development' : DevelopmentConfig,
    'test' : TestConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig,
    'heroku' : HerokuConfig,
}