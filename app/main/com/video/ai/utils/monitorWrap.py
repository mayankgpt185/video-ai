import datetime
from flask import request
from functools import wraps

def monitor(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        s = datetime.datetime.now()
        _ = function(*args, **kwargs)
        e = datetime.datetime.now()
        return _
    return wrapper