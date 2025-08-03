from requests import get
from flask import make_response, redirect

from environment import API_URL, customInvalidResponse

def get_url(url:str, headers={}):
        return get(url=f'{API_URL}{url}', headers=headers)
    
def error_404():
    return make_response("404", 404)

def invalidResponse():
    if isinstance(customInvalidResponse, str):
        return make_response(redirect(customInvalidResponse))
    elif isinstance(customInvalidResponse, int):
        return make_response(str(customInvalidResponse), customInvalidResponse)
    elif isinstance(customInvalidResponse, bool):
        return error_404()
    return error_404()