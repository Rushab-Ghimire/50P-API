import graphene
from graphene_django import DjangoObjectType
from card.models import ContextCard
from django.db.models import Q
from authtf.models import UIModelType
from pubsub.consumer import PubSubBroadcaster
import random

class ContextCardType(DjangoObjectType):
  class Meta:
    model = ContextCard
    fields = ("__all__")

class ContextCardDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(ContextCardType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  card = graphene.Field(ContextCardDataModelType,
                        key=graphene.Int(),
                        parent=graphene.Int(), organization_id=graphene.Int())
  card_children = graphene.Field(ContextCardDataModelType,
                        parent=graphene.Int(), organization_id=graphene.Int())
  card_by_key = graphene.Field(ContextCardDataModelType,
                        key=graphene.String(), organization_id=graphene.Int())
  card_tree_by_key = graphene.Field(ContextCardDataModelType,
                        key=graphene.String(), organization_id=graphene.Int())
  card_ui = graphene.Field(UIModelType)

  card_by_message = graphene.Field(ContextCardDataModelType,
                        message=graphene.String())

  def resolve_card_ui(self, info):
    import json
    with open('./uiservice/ui/card/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'card', ui = o)
    return d

  def resolve_card_children(self, info, parent,  **kwargs):
    organization_id = kwargs.get("organization_id", -1)
    if organization_id == -1:
      organization_id = 1
    qs = ContextCard.objects.filter(
        is_deleted = False,
        organization_id=organization_id,
        parent = parent
        )
    totalCount = qs.count()
    d = ContextCardDataModelType(totalCount = totalCount, rows = qs)
    return d

  def resolve_card_by_key(self, info, key, **kwargs):
    organization_id = kwargs.get("organization_id", -1)
    if organization_id == -1:
      organization_id = 1
    qs = ContextCard.objects.filter(
                                    Q(context=key),
                                    organization_id=organization_id,
                                    is_deleted = False
                                )

    totalCount = qs.count()
    d = ContextCardDataModelType(totalCount = totalCount, rows = qs)
    return d

  def resolve_card_tree_by_key(self, info, key, **kwargs):
    # qs_parent = ContextCard.objects.filter(
    #                                 Q(context=key),
    #                                 is_deleted = False
    #                                 ).first()
    # qs = Query.recursiveCall(qs_parent.pk)
    # qs_detached = ContextCard.objects.filter(
    #     is_deleted = False,
    #     parent = 0
    #     )
    # qs = qs.union(qs_detached)
    
    organization_id = kwargs.get("organization_id", -1)
    if organization_id == -1:
      organization_id = 1

    qs = ContextCard.objects.filter(Q(organization_id=organization_id), is_deleted = False)

    totalCount = qs.count()
    d = ContextCardDataModelType(totalCount = totalCount, rows = qs)
    return d

  def resolve_card_by_message(self, info, message, **kwargs):

    message_parts = message


    all_ = False

    all_filter = ["all", "feature", "menu", "help"]
    if any(x in message_parts for x in all_filter):
      all_ = True

    notify_filter = ["notify"]
    if any(x in message_parts for x in notify_filter):
      PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_NOTIFICATION",
            "payload": {
              "id" : random.randint(10,100),
              "user_id" : random.randint(10,100),
              "imgUrl" : "domnic-harris.jpg",
              "userTitle": f"User {random.randint(10,100)}",
              "message" : f"Insightful Notification - {random.randint(10,100)}"
            }
          }
        )

    notify_filter = ["message"]
    if any(x in message_parts for x in notify_filter):
      PubSubBroadcaster.broadcast("common",
          {
            "event_name": "NEW_MESSAGE",
            "payload": {
              "id" : random.randint(10,100),
              "user_id" : random.randint(10,100),
              "imgUrl" : "domnic-harris.jpg",
              "userTitle": f"User {random.randint(10,100)}",
              "message" : f"Insightful Notification - {random.randint(10,100)}"
            }
          }
        )

    qs = ContextCard.objects.none()
    if not all_:
      search = message.split(" ")
      qs_final = ContextCard.objects.none()
      for key in search:
        qs = ContextCard.objects.filter(is_deleted = False)
        filter = (
                #Q(context__icontains=key) |
                #Q(title__icontains=key) |
                Q(description__icontains=key)
            )
        qs = qs.filter(filter)
        qs_final = qs_final.union(qs)
    else:
      qs_final = qs

    totalCount = qs_final.count()

    if totalCount == 0:
      qs_final = ContextCard.objects.filter(is_deleted = False)

    d = ContextCardDataModelType(totalCount = qs_final.count(), rows = qs_final)
    return d

  def resolve_card(self, info, key, parent = None,  **kwargs):

    organization_id = kwargs.get("organization_id", -1)
    if organization_id == -1:
      organization_id = 1

    if key != -1:
      try:
        qs = ContextCard.objects.filter(
                                                Q(pk=key),
                                                Q(organization_id=organization_id),
                                                is_deleted = False
                                               )
      except ContextCard.DoesNotExist:
        pass

    if parent != 0:
      qs = Query.recursiveCall(parent)
      qs_detached = ContextCard.objects.filter(
          is_deleted = False,
          organization_id=organization_id,
          parent = 0
          )
      qs = qs.union(qs_detached)

    totalCount = qs.count()
    d = ContextCardDataModelType(totalCount = totalCount, rows = qs)
    return d

  def recursiveCall(parent):
    qs = ContextCard.objects.filter(
          is_deleted = False,
          parent = parent
          )
    qs_subtree = ContextCard.objects.none()
    if qs.first() != None:
      for item in qs:
        qs_subtree = qs_subtree.union(Query.recursiveCall(item.pk))
      qs = qs.union(qs_subtree)
    else:
      return ContextCard.objects.none()

    return qs


class CreateCard(graphene.Mutation):
  class Arguments:
    title = graphene.String()
    description = graphene.String()
    context = graphene.String()
    parent = graphene.Int()
    organization_id = graphene.Int()

  ok = graphene.Boolean()
  card = graphene.Field(ContextCardType)
  def mutate(self, info, title, description, context, parent, organization_id):
    card = ContextCard( title=title,
                        description=description,
                        context = context,
                        parent = parent,
                        organization_id = organization_id
                      )
    card.save()
    return CreateCard(ok=True, card=card)


class DeleteCard(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    try:
        card = ContextCard.objects.get(pk=id)
    except ContextCard.DoesNotExist:
        raise Exception("Card does not exist")
    card.is_deleted = True
    card.save()
    return DeleteCard(ok=True)


class UpdateCard(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String(required=False)
    context = graphene.String(required=False)
    parent = graphene.Int(required=False)

  ok = graphene.Boolean()
  card = graphene.Field(ContextCardType)

  def mutate(self, info, id, title, **kwargs):
    parent = kwargs.get("parent", 0)
    context = kwargs.get("context", None)
    description = kwargs.get("description", None)
    try:
        card = ContextCard.objects.get(pk=id)
    except ContextCard.DoesNotExist:
        raise Exception("Card does not exist")

    card.title = title

    if description : card.description = description
    if context : card.context = context
    if parent != 0 : card.parent = parent

    card.save()
    return UpdateCard(ok=True, card=card)


class UpdateCardGraph(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    graph_attributes = graphene.String()

  ok = graphene.Boolean()
  card = graphene.Field(ContextCardType)

  def mutate(self, info, id, graph_attributes, **kwargs):
    try:
        card = ContextCard.objects.get(pk=id)
    except ContextCard.DoesNotExist:
        raise Exception("Card does not exist")

    card.graph_attributes = graph_attributes
    card.save()
    return UpdateCardGraph(ok=True, card=card)

class DetachCard(graphene.Mutation):
  class Arguments:
    id = graphene.Int()

  ok = graphene.Boolean()
  card = graphene.Field(ContextCardType)

  def mutate(self, info, id, **kwargs):
    try:
        card = ContextCard.objects.get(pk=id)
    except ContextCard.DoesNotExist:
        raise Exception("Card does not exist")

    card.parent = 0
    card.save()
    return DetachCard(ok=True, card=card)


class AttachCard(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    parent = graphene.Int()

  ok = graphene.Boolean()
  card = graphene.Field(ContextCardType)

  def mutate(self, info, id, parent, **kwargs):
    try:
        card = ContextCard.objects.get(pk=id)
    except ContextCard.DoesNotExist:
        raise Exception("Card does not exist")

    card.parent = parent
    card.save()
    return AttachCard(ok=True, card=card)

class Mutation(graphene.ObjectType):
  create_card = CreateCard.Field()
  delete_card = DeleteCard.Field()
  update_card = UpdateCard.Field()
  update_card_graph = UpdateCardGraph.Field()
  detach_card = DetachCard.Field()
  attach_card = AttachCard.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
