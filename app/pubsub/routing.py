from django.urls import re_path, path


from . import consumer

websocket_urlpatterns = [
    re_path(r"ws/event/(?P<channel>\w+)/$", consumer.PubSubConsumer.as_asgi()),
]

