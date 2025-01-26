from flask import request, current_app, Response
from flask_restx import Namespace, Resource
from app.main.com.video.ai.dto.videoDTO import videoDTO
from app.main.com.video.ai.service.VideoService import VideoService
from app.main.com.video.ai.utils.monitorWrap import monitor
from flask import Response ,json

api = videoDTO.api
@api.route('/')
class VideoController(Resource):
    api = videoDTO.api
    _payload = videoDTO.payload
    @api.response(201, 'video script request sent successfully .')
    # @api.doc('create outcomes')
    @api.expect(_payload, validate=True)
    def post(self)-> Response:
        appConfig = dict(current_app.config)
        # headers = dict(request.headers)
        vs = VideoService(appConfig)
        data = request.json
        outcomeData = vs.createVideoScript(data["topic"], data["sceneCount"],appConfig=appConfig)
        return Response(
        response= json.dumps(outcomeData),
        status=201,
        mimetype='application/json'
        )
