import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Student
from django.core.exceptions import ValidationError


class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        fields = ["id", "first_name"]


class StudentResponseModel(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(StudentType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):

    student = graphene.Field(StudentResponseModel)

    student_by_id = graphene.Field(StudentType, id=graphene.Int())

    def resolve_student(self, info, **kwargs):
        filter = Q()
        qs = Student.objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        return StudentResponseModel(totalCount=totalCount, rows=qs)

    def resolve_student_by_id(self, info, id):
        return Student.objects.get(pk=id)


class CreateStudent(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)

    student = graphene.Field(StudentType)

    def mutate(self, info, first_name):
        student = Student.objects.create(
            first_name=first_name
        )
        return CreateStudent(student=student)


class UpdateStudent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        first_name = graphene.String()

    student = graphene.Field(StudentType)

    def mutate(self, info, id, **kwargs):
        try:
            item = Student.objects.get(pk=id)
        except Student.DoesNotExist:
            raise ValidationError("Student does not exist")

        item.first_name = kwargs.get("first_name", item.first_name)
        item.save(
            update_fields=[
                "first_name",
            ]
        )
        return UpdateStudent(student=item)


class DeleteStudent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    def mutate(self, info, id):
        item = Student.objects.get(pk=id)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteStudent(ok=True)


class Mutation(graphene.ObjectType):
    student_add = CreateStudent.Field()
    student_update = UpdateStudent.Field()
    student_delete = DeleteStudent.Field()


student_schema = graphene.Schema(query=Query, mutation=Mutation)
