import graphene
from graphene_django import DjangoObjectType
from django.db import models
from django.conf import settings
import json
from openai import OpenAI

class ReplyModel(models.Model):
    messageOut = models.TextField(blank=True)
    context = models.JSONField(blank=True)

    class Meta:
        managed = False

class ReplyModelType(DjangoObjectType):
  class Meta:
    model = ReplyModel
    fields = ("messageOut", "context")

class Query(graphene.ObjectType):
  tfa_reply = graphene.Field(ReplyModelType,
                        messageIn=graphene.String())

  def resolve_tfa_reply(self, info, messageIn, **kwargs):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": messageIn
            }
        ]
    )

    context = {
      "context" : "help",
    }

    # return ReplyModelType(context = json.dumps(context),
    #                     messageOut = f"reply to {messageIn}")

    #print(completion.choices[0].message)

    d = ReplyModelType(context = json.dumps(context),
                       messageOut = completion.choices[0].message.content)

    return d

schema_bot = graphene.Schema(query=Query)
