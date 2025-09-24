import graphene
from graphene_django import DjangoObjectType
from core.models import Message
from authtf.models import UIModelType
from django.db.models import Q
from pubsub.consumer import PubSubBroadcaster

class MessageType(DjangoObjectType):
  class Meta:
    model = Message
    fields = ("__all__")

class MessageDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(MessageType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  message = graphene.Field(
      MessageDataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  message_by_id = graphene.Field(MessageType, id=graphene.Int())

  def resolve_message_by_id(root, info, id):
    return Message.objects.get(pk = id, is_deleted=False)

  def resolve_message(self, info, **kwargs):
    qs = Message.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(message__icontains=search)
        )
        qs = qs.filter(filter)
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = MessageDataModelType(totalCount = totalCount, rows = qs)
    return d

class CreateMessage(graphene.Mutation):
  class Arguments:
    message = graphene.String()

  ok = graphene.Boolean()
  message = graphene.Field(MessageType)
  def mutate(self, info, message):

    notify_filter = ["tax-filing", "tips", "marketing", "sales"]
    x = next((x for x in notify_filter if x in message), None)
    if x != None:
      if x == "marketing":
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "MARKETING",
              "action": x.upper(),
              "message" : f"Slow month ahead. Let’s prepare!."
            }
          }
        )

      if x == "sales":
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "SALES",
              "action": x.upper(),
              "message" : f"Log my Sales and Tips for Customer David."
            }
          }
        )

      if x == "tax-filing":
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "PROCESS",
              "action": x.upper(),
              "message" : f"Tax filing season is here! Automate your filings now."
            }
          }
        )

      if x == "tips":
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "TIPS-ACT",
              "action": x.upper(),
              "message" : f"You’ve logged significant travel expenses. Did you know you can deduct business mileage?"
            }
          }
        )
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "TIPS-LEARN",
              "action": x.upper(),
              "message" : f"Your recent equipment purchases may qualify for depreciation deductions."
            }
          }
        )
        PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "event_type": "TIPS-ACT",
              "action": x.upper(),
              "message" : f"Consider setting up a retirement account for added tax benefits this quarter."
            }
          }
        )



    message = Message(
                            message=message,
                        )
    message.save()
    return CreateMessage(ok=True, message=message)


class DeleteMessage(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    try:
        message = Message.objects.get(id)
    except Message.DoesNotExist:
        raise Exception("Process does not exist")
    message.is_deleted = True
    return DeleteMessage(ok=True)


class UpdateMessage(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    message = graphene.String()

  ok = graphene.Boolean()
  message = graphene.Field(MessageType)

  def mutate(self, info, id, message):
    try:
        message = Message.objects.get(pk = id)
    except Message.DoesNotExist:
        raise Exception("Message does not exist")

    message.message=message
    message.save()
    return UpdateMessage(ok=True, message=message)

class Mutation(graphene.ObjectType):
  create_message = CreateMessage.Field()
  delete_message = DeleteMessage.Field()
  update_message = UpdateMessage.Field()


schema_message = graphene.Schema(query=Query, mutation=Mutation)
