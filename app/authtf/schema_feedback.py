import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from authtf.models import Feedback
from salon.models import Order
from django.db.models import Q


class FeedbackType(DjangoObjectType):
    class Meta:
        model = Feedback
        fields = ["id", "unique_id", "order", "rating", "comment", "user"]


class FeedbackDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(FeedbackType)

    class Meta:
        fields = ["totalCount", "rows"]


class Query(graphene.ObjectType):
    feedback = graphene.Field(
        FeedbackDataModelType,
        order_id=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    feedback_by_id = graphene.Field(FeedbackType, id=graphene.Int(required=True))
    feedback_by_code = graphene.Field(FeedbackType, code=graphene.String(required=True))

    def resolve_feedback(self, info, **kwargs):
        order_id = kwargs.get("order_id")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        filter = Q()

        if order_id:
            filter = Q(order_id=order_id)

        qs = Feedback.objects.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return FeedbackDataModelType(totalCount=totalCount, rows=qs)

    def resolve_feedback_by_id(self, info, id):
        return Feedback.objects.get(pk=id)

    def resolve_feedback_by_code(self, info, code):
        return Feedback.objects.get(unique_id=code)


class CreateFeedback(graphene.Mutation):
    feedback = graphene.Field(FeedbackType)

    class Arguments:
        unique_id = graphene.String(required=True)
        order_id = graphene.Int(required=True)
        rating = graphene.Float(required=True)
        comment = graphene.String(required=False)

    @login_required
    def mutate(self, info, unique_id, order_id, rating, comment=None):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise Exception("Order does not exist")

        feedback = Feedback.objects.create(
            unique_id=unique_id,
            order=order,
            rating=rating,
            comment=comment,
            organization=org,
            user=session_user,
        )

        return CreateFeedback(feedback=feedback)


class UpdateFeedback(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        unique_id = graphene.String()
        order_id = graphene.Int()
        rating = graphene.Float()
        comment = graphene.String()

    feedback = graphene.Field(FeedbackType)

    @login_required
    def mutate(self, info, id, **kwargs):
        item = Feedback.objects.get(pk=id)

        order_id = kwargs.get("order_id")
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise Exception("Order does not exist")

        item.unique_id = kwargs.get("unique_id", item.unique_id)
        item.order = order if order else item.order
        item.rating = kwargs.get("rating", item.rating)
        item.comment = kwargs.get("comment", item.comment)

        item.save(
            update_fields=[
                "unique_id",
                "order",
                "rating",
                "comment",
            ]
        )
        return UpdateFeedback(feedback=item)

class SubmitFeedback(graphene.Mutation):
    class Arguments:
        unique_id = graphene.String()
        rating = graphene.Float()
        comment = graphene.String()

    feedback = graphene.Field(FeedbackType)

    def mutate(self, info, unique_id, **kwargs):
        item = Feedback.objects.get(unique_id=unique_id)
        item.rating = float(kwargs.get("rating", item.rating))
        item.comment = kwargs.get("comment", item.comment)

        item.save(
            update_fields=[
                "rating",
                "comment",
            ]
        )
        return UpdateFeedback(feedback=item)


class DeleteFeedback(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    def mutate(self, info, id):
        item = Feedback.objects.get(pk=id)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteFeedback(ok=True)


class Mutation(graphene.ObjectType):
    create_feedback = CreateFeedback.Field()
    update_feedback = UpdateFeedback.Field()
    delete_feedback = DeleteFeedback.Field()
    submit_feedback = SubmitFeedback.Field()



schema_feedback = graphene.Schema(query=Query, mutation=Mutation)
