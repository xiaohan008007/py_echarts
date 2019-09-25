import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    dbargs = {"host": "192.168.3.57", "username": "danqing", "password": "danqing123", "dbname": "tts_tob_qly_v2"}
    connect = "mysql+pymysql://{username}:{password}@{host}/{dbname}?charset=utf8"
    SQLALCHEMY_DATABASE_URI = connect.format(**dbargs)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUEST_STATS_WINDOW = 15


class DevelopmentConfig(Config):
    DEBUG = True
    QLY = True
    ZHISHU99 = False


class ProductionConfig(Config):
    DEBUG = False
    QLY = True
    ZHISHU99 = False


class TestingConfig(Config):
    TESTING = True
    dbargs = {"host": "199.155.122.203", "username": "root", "password": "myroot", "dbname": "tts_tob_qly_v2"}
    connect = "mysql+pymysql://{username}:{password}@{host}/{dbname}?charset=utf8"
    SQLALCHEMY_DATABASE_URI = connect.format(**dbargs)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
