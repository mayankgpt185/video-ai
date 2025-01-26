import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    
    # MONGODB SETTINGS
    MONGODB_SETTINGS = 'localhost'
    MONGODB_HOST = ''
    MONGODB_PORT = ''
    MONGODB_DB = '' 

class DevelopmentConfig(Config):

    DEBUG = True   
    
config_by_name = dict(
    dev=DevelopmentConfig,
)

key = Config.SECRET_KEY