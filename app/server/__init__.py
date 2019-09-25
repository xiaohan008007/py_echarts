import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append("..")
from app.config import config


db = SQLAlchemy()
# from . import models


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLACK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # app.after_request(after_request)
    CORS(app)

    db.init_app(app)

    # Register web application routes
    from .main_server import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册QLY图表接口
    if config["production"].QLY:
        from .qly_api import app as api_blueprint
        app.register_blueprint(api_blueprint)

        from .douyin_api import app as douyin_blueprint
        app.register_blueprint(douyin_blueprint)

    # # 注册电商词性接口
    # if config["production"].PROPS:
    #     from .props_api import props_api as props_blueprint
    #     app.register_blueprint(props_blueprint)
    #
    # # 注册精准推荐词接口
    # if config["production"].RECOMM:
    #     from .recomm_api import recomm_api as recomm_blueprint
    #     app.register_blueprint(recomm_blueprint)
    return app
