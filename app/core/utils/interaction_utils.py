from core.utils.request_utils import post_request
from django.conf import settings


class InteractionUtils:
    base_url = settings.INTERACTION_URL

    @classmethod
    def get_keywords_for_content(cls, content):
        url = f"{cls.base_url}/keywords-from-text"

        payload = {"text": content}

        response = post_request(url, payload)

        return response.json()
