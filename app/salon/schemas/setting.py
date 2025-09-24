import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from salon.models import (
    Setting,
)
from organization.models import Organization
from graphql_jwt.decorators import login_required


class SettingType(DjangoObjectType):
    class Meta:
        model = Setting
        fields = ["id", "key", "value"]


class SettingDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(SettingType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_setting = graphene.Field(
        SettingDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_setting_by_id = graphene.Field(SettingType, id=graphene.Int(required=True))
    salon_setting_by_organization_id = graphene.Field(
        SettingDataModelType, keys=graphene.List(graphene.String)
    )

    @login_required
    def resolve_salon_setting(self, info, **kwargs):
        org = info.context.user.get_organization()

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(key__icontains=search) | Q(value__icontains=search)

        qs = Setting.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return SettingDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_salon_setting_by_id(root, info, id):
        org = info.context.user.get_organization()
        return Setting.objects.get(pk=id, organization=org)

    @login_required
    def resolve_salon_setting_by_organization_id(root, info, keys):
        try:
            org = info.context.user.get_organization()
        except Organization.DoesNotExist:
            raise Exception("Organization does not exist.")

        key = ""
        sts = 0
        for i in range(len(keys)):
            key = keys[i]
            sts = Setting.objects.filter(organization=org, key=key)
            if(sts.count() <= 0):
                item = Setting(key=key, value="", organization=org)
                item.save()

        qs = Setting.objects.filter(organization=org)
        totalCount = qs.count()
        return SettingDataModelType(totalCount=totalCount, rows=qs)


class CreateSalonSetting(graphene.Mutation):
    class Arguments:
        key = graphene.String(required=True)
        value = graphene.String(required=True)

    ok = graphene.Boolean()
    setting = graphene.Field(SettingType)

    @login_required
    def mutate(self, info, key, value):
        session_user = info.context.user
        org = session_user.get_organization()

        item = Setting(key=key, value=value, organization=org, user=session_user)
        item.save()
        return CreateSalonSetting(ok=True, setting=item)


class UpdateSalonSetting(graphene.Mutation):
    class Arguments:
        keys = graphene.List(graphene.String)
        values = graphene.List(graphene.String)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, keys, values):
        try:
            org = info.context.user.get_organization()
        except Organization.DoesNotExist:
            raise Exception("Organization does not exist.")

        for i in range(len(keys)):
            key = keys[i]
            value = values[i]
            try:
                item = Setting.objects.get(key=key, organization=org)
                item.value = value
                item.save()
            except Setting.DoesNotExist:
                pass


        return UpdateSalonSetting(ok=True)


class Mutation(graphene.ObjectType):
    salon_setting_create = CreateSalonSetting.Field()
    salon_setting_update = UpdateSalonSetting.Field()


schema_salon_setting = graphene.Schema(query=Query, mutation=Mutation)
