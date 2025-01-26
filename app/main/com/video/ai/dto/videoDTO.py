from flask_restx import Namespace ,fields

class videoDTO(object):
    api = Namespace('video', description='video related operations')
    payload = api.model('video', {
        "topic": fields.String(required=True, description='topic'),
        "sceneCount": fields.Integer(required=True, description='sceneCount')
    })