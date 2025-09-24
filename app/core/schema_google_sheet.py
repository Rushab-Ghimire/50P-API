import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from salon.models import (
    FloorPlan,
)
from core.utils import google_sheet

class GoogleSheetAddRow(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        row = [kwargs.get("name"), kwargs.get("phone_number")]
        google_sheet.add_row(row)

        return GoogleSheetAddRow(ok=True)


class Mutation(graphene.ObjectType):
    google_sheet_add_row = GoogleSheetAddRow.Field()


schema_google_sheet = graphene.Schema(mutation=Mutation)
