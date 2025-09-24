import os
from pubsub.consumer import PubSubBroadcaster
import ad.schemas.notification as notification


class NotificationUtils:
    def notify(title, message, toUser, context, event_type = "QUEUE", n_type = "common", data_string = ""):
        res = notification.notification_schema.execute(
                '''
                mutation MyMutation {
                    notificationAdd(content: "%s", toUser: %d, dataString: "%s") {
                        notification {
                            id
                        }
                    }
                }
                ''' % (message, toUser, data_string),
                context=context
            )

        PubSubBroadcaster.broadcast(n_type,
            {
                "event_name": "NEW_NOTIFICATION",
                "payload": {
                    "id" : res.data["notificationAdd"]["notification"]["id"],
                    "event_type" : event_type,
                    "userTitle": f"{title}",
                    "message" : f"{message}"
                }
            }
        )


    def notify_without_history(toBooking, toUser, n_type = "common"):
        PubSubBroadcaster.broadcast(n_type,
            {
                "event_name": "NEW_NOTIFICATION",
                "payload": {
                    "booking_id" : toBooking,
                    "event_type" : "IS_TYPING",
                    "receiver_id": toUser
                }
            }
        )

    def message_without_history(toBooking, toUser, message, n_type = "common"):
        PubSubBroadcaster.broadcast(n_type,
            {
                "event_name": "NEW_NOTIFICATION",
                "payload": {
                    "booking_id" : toBooking,
                    "event_type" : "POSTED_MESSAGE",
                    "receiver_id": toUser,
                    "message": message
                }
            }
        )
