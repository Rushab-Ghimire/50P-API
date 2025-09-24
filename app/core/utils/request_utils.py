import requests


def post_request(url, payload, headers=None):
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    response = requests.post(url, json=payload, headers=default_headers)
    return response
