from requests import get, post
from flask import make_response, redirect

from environment import API_URL, customInvalidResponse, config

def get_url(url:str, headers={}, stream=False):
        return get(url=f'{API_URL}{url}', headers=headers, stream=stream)
    
def post_url(url:str, json:str, headers={}, stream=False):
    return post(url=f'{API_URL}{url}', headers=headers, json=json, stream=stream)

def error_404():
    r = make_response("404", 404)
    r.headers = config['ipp']['responseHeaders']
    return r

def invalidResponse():
    if isinstance(customInvalidResponse, str):
        return make_response(redirect(customInvalidResponse))
    elif isinstance(customInvalidResponse, int):
        return make_response(str(customInvalidResponse), customInvalidResponse)
    elif isinstance(customInvalidResponse, bool):
        return error_404()
    return error_404()