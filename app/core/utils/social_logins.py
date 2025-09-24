import requests


def get_google_user_info(token):
    url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
    return requests.get(url, headers={"Content-Type": "application/json"})
