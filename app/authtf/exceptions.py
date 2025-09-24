from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):

    res = exception_handler(exc, context)
    try:
        message = res.data['detail']
        res.data = {
            'error' : res.data['detail']
        }
    except:
        if exc.__class__.__name__ == 'ValidationError':
            res.data = {
                'error' : res.data
            }

    return res
