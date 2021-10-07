'''

    app 初始化建構式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/05
    update by : jay

'''

from flask import Flask, config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# ----- 自訂函式 -----
from config import config

# 初始化套件
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name : str) -> Flask:
    ''' 根據不同的設定參數，產生不同的 Flask 實例 '''

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as authblueprint
    app.register_blueprint(authblueprint, url_prefix = '/auth')

    return app