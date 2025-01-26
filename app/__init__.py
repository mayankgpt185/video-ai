from flask_restx import Api
from flask import Blueprint

from .main.com.video.ai.controller.VideoController import api as video

contextURL='/video-ai'	
blueprint = Blueprint('api', __name__,url_prefix=contextURL)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    blueprint,
    title='All I Want',
    version='1.0',
    description='Trying something hope u like it!!!',
    authorizations=authorizations,
    security='apikey',
    doc='/docs/'
)

api.add_namespace(video, path='/video')
