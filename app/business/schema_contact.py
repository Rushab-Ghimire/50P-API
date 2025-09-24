import graphene
from graphene_django import DjangoObjectType
from business.models import Contact
from authtf.models import UIModelType
from django.db.models import Q


class ContactType(DjangoObjectType):
  class Meta:
    model = Contact
    fields = ("__all__")

class ContactDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(ContactType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  contact = graphene.Field(
      ContactDataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  contact_by_id = graphene.Field(ContactType, id=graphene.Int())
  contact_ui = graphene.Field(UIModelType)

  def resolve_contact(self, info, **kwargs):
    qs = Contact.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
        qs = qs.filter(filter)

    qs = qs.order_by("-modified_date")
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = ContactDataModelType(totalCount = totalCount, rows = qs)
    return d


  def resolve_contact_ui(self, info):
    import json
    with open('./uiservice/ui/contact/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'contact', ui = o)
    return d

  def resolve_contact_by_id(root, info, id):
    return Contact.objects.get(pk = id, is_deleted=False)

class CreateContact(graphene.Mutation):
  class Arguments:
    first_name = graphene.String(required=True)
    last_name = graphene.String()
    email = graphene.String(required=True)
    primary_phone = graphene.String()
    primary_address = graphene.String()

  ok = graphene.Boolean()
  contact = graphene.Field(ContactType)
  def mutate(self, info, first_name, email, **kwargs):
    last_name = kwargs.get("last_name", "")
    primary_phone = kwargs.get("primary_phone", "")
    primary_address = kwargs.get("primary_address", "")
    contact = Contact(first_name=first_name,
                      last_name=last_name,
                      email=email,
                      primary_phone = primary_phone,
                      primary_address = primary_address
                      )
    contact.save()
    return CreateContact(ok=True, contact=contact)

class DeleteContact(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    contact = Contact.objects.get(pk=id)
    contact.is_deleted = True
    contact.save();
    return DeleteContact(ok=True)


class UpdateContact(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    first_name = graphene.String(required=True)
    last_name = graphene.String()
    email = graphene.String(required=True)
    primary_phone = graphene.String()
    primary_address = graphene.String()

  ok = graphene.Boolean()
  contact = graphene.Field(ContactType)

  def mutate(self, info, id, first_name, email, **kwargs):
    last_name = kwargs.get("last_name", "")
    primary_phone = kwargs.get("primary_phone", "")
    primary_address = kwargs.get("primary_address", "")
    contact = Contact.objects.get(pk = id)
    contact.first_name = first_name
    contact.last_name = last_name
    contact.email = email
    contact.primary_phone = primary_phone
    contact.primary_address = primary_address
    contact.save()
    return UpdateContact(ok=True, contact=contact)

class Mutation(graphene.ObjectType):
  create_contact = CreateContact.Field()
  delete_contact = DeleteContact.Field()
  update_contact = UpdateContact.Field()


schema_contact = graphene.Schema(query=Query, mutation=Mutation)
