import graphene
from graphene_django import DjangoObjectType
from graphene.types.json import JSONString
from salon.models import *
from organization.models import *
import re
from datetime import datetime
from pubsub.consumer import PubSubBroadcaster
from salon.models.setting import get_tax_settings
from core.utils.tf_utils import (
    get_amount_with_currency_code,
    get_customer_file_URL,
    convert_string_to_float,
)
from django.db.models import Q
from graphql_jwt.decorators import login_required
from salon.schemas.selectors import SelectorDataModelType
from salon.schemas.queue import QueueType
import random
from core.utils import google_sheet

class Query(graphene.ObjectType):
    salon_ds = graphene.Field(
        SelectorDataModelType
    )

    def resolve_salon_ds(self, info, **kwargs):
        DS = {}
        totalCount = 1

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d

class EhrAiRecord(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        contact = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        note = graphene.String()
        org_id = graphene.Int()

    q_item = graphene.Field(QueueType)

    def mutate(self, info, **kwargs):
        org_id = kwargs.get("org_id", -1)
        name = kwargs.get("name", None)
        note = kwargs.get("note", None)
        contact = kwargs.get("contact", None)
        email = kwargs.get("email", "")
        phone = kwargs.get("phone", "")

        print("org_id", org_id)

        row = [name, note, contact, email, phone, org_id]
        print(row)
        google_sheet.add_row(row)
        PubSubBroadcaster.broadcast("common",
            {
                "event_name": "NEW_NOTIFICATION",
                "payload": {
                "id" : "g5",
                "event_type" : "QUEUE",
                "userTitle": f"TileFlexAI",
                "message" : f"Google Sheet for Booking Updated"
                }
            }
        )
        return EhrAiRecord(q_item={})


class Mutation(graphene.ObjectType):
    ehr_ai_booking = EhrAiRecord.Field()

schema_ehr_ai_queue = graphene.Schema(query=Query, mutation=Mutation)
