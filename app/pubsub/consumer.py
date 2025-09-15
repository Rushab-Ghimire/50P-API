import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

class PubSubBroadcaster:
    @staticmethod
    def broadcast(channel, payload):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"channel_{channel}",
            {
                "type": "channel.message",
                "message": payload
            }
        )


class PubSubConsumer(WebsocketConsumer):
    def connect(self):
        self.ch_name = self.scope["url_route"]["kwargs"]["channel"]
        self.ch_group_name = f"channel_{self.ch_name}"
        # Join channel group
        async_to_sync(self.channel_layer.group_add)(
            self.ch_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave channel group
        async_to_sync(self.channel_layer.group_discard)(
            self.ch_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to channel group
        async_to_sync(self.channel_layer.group_send)(
            self.ch_group_name, {"type": "channel.message", "message": message}
        )

    # Receive message from channel group
    def channel_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))