
import os
import traceback
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from config import config
if config.gpu_disabled:
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import core.api as API
import auth

from flask import request, send_file
from flask_api import FlaskAPI, status, exceptions
app = FlaskAPI(__name__)

tokens = auth.read_tokens()

@app.before_request
def validate_token():
    url = request.base_url
    extensions = ('.css', '.js', '.ico')
    if '/drawings' in url:
        pass
    elif '/documents' in url:
        pass
    elif url.endswith(extensions):
        pass
    else:
        token = request.args.to_dict().get('token')
        if not token in tokens:
            return not_allowed('Invalid access token.')


################################ SEARCH ROUTES ################################

@app.route('/search/102/', methods=['GET'])
def search_102():
    return create_request_and_serve(request, API.SearchRequest102)

@app.route('/search/103/', methods=['GET'])
def seach_103():
    return create_request_and_serve(request, API.SearchRequest103)

@app.route('/prior-art/patent/', methods=['GET'])
def get_patent_prior_art():
    return create_request_and_serve(request, API.PatentPriorArtRequest)

@app.route('/similar/', methods=['GET'])
def get_similar_patents():
    return create_request_and_serve(request, API.SimilarPatentsRequest)

@app.route('/snippets/', methods=['GET'])
def get_snippet():
    return create_request_and_serve(request, API.SnippetRequest)

@app.route('/mappings/', methods=['GET'])
def get_mapping():
    return create_request_and_serve(request, API.MappingRequest)

@app.route('/datasets/', methods=['GET'])
def get_sample():
    return create_request_and_serve(request, API.DatasetSampleRequest)

@app.route('/extension/', methods=['GET'])
def handle_incoming_ext_request():
    return create_request_and_serve(request, API.IncomingExtensionRequest)


################################# DATA ROUTES #################################

@app.route('/documents/', methods=['GET'])
def get_document():
    return create_request_and_serve(request, API.DocumentRequest)

@app.route('/patents/<pn>/drawings/<n>/', methods=['GET'])
def get_patent_drawing(pn, n):
    try:
        local_path = API.DrawingRequest({'pn': pn, 'n': n}).serve()
        return send_file(local_path, mimetype='image/jpeg')
    except Exception as err:
        traceback.print_exc()
        return bad_request(err.message)

@app.route('/patents/<pn>/drawings/', methods=['GET'])
def list_patent_drawings(pn):
    try:
        return API.ListDrawingsRequest({'pn': pn}).serve()
    except Exception as err:
        traceback.print_exc()
        return bad_request(err.message)

############################### ROUTES END HERE ###############################

def create_request_and_serve(req, reqClass):
    try:
        if isinstance(req, dict):
            req_data = req
        else:
            req_data = req.args.to_dict()
        return success(reqClass(req_data).serve())
    except API.BadRequestError as err:
        traceback.print_exc()
        return bad_request(err.message)
    except API.ServerError as err:
        traceback.print_exc()
        return server_error(err.message)
    except API.NotAllowedError as err:
        traceback.print_exc()
        return not_allowed(err.message)

def success(response):
    return response, status.HTTP_200_OK

def server_error(msg=None):
    msg = msg if msg else 'Server error'
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    return msg, http_status

def bad_request(msg=None):
    msg = msg if msg else 'Bad request'
    http_status = status.HTTP_400_BAD_REQUEST
    return msg, http_status

def not_allowed(msg=None):
    msg = msg if msg else 'Request disallowed.'
    http_status = status.HTTP_403_FORBIDDEN
    return msg, http_status

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=config.port)

