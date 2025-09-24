import graphene
from graphene_django import DjangoObjectType
from salon.models import Session, SessionStatus, Pos, Beautician, Booking
from graphql_jwt.decorators import login_required


class SessionType(DjangoObjectType):
    class Meta:
        model = Session
        fields = [
            "id",
            "open_date_time",
            "close_date_time",
            "pos",
            "beautician",
            "status",
            "booking",
        ]


class SessionStatusType(DjangoObjectType):
    class Meta:
        model = SessionStatus
        fields = ["id", "title"]


class PosType(DjangoObjectType):
    class Meta:
        model = Pos
        fields = ["id", "title"]


class BeauticianType(DjangoObjectType):
    class Meta:
        model = Beautician
        fields = ["id", "linked_user", "phone"]


class SessionDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(SessionType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_session = graphene.Field(
        SessionDataModelType,
        # search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_session_by_id = graphene.Field(SessionType, id=graphene.Int())

    @login_required
    def resolve_salon_session(self, info, **kwargs):
        # search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        # filter = Q()
        # if search:
        #     filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = Session.objects.filter(organization=org)
        # qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return SessionDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_salon_session_by_id(root, info, id):
        org = info.context.user.get_organization()
        return Session.objects.get(pk=id, organization=org)


class CreateSalonSession(graphene.Mutation):
    class Arguments:
        open_date_time = graphene.DateTime(required=True)
        close_date_time = graphene.DateTime(required=True)
        pos_id = graphene.Int()
        beautician_id = graphene.Int()
        status_id = graphene.Int()
        booking_id = graphene.Int()

    ok = graphene.Boolean()
    session = graphene.Field(SessionType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        pos_id = kwargs.get("pos_id")
        pos = None
        if pos_id:
            try:
                pos = Pos.objects.get(pk=pos_id, organization=org)
            except Pos.DoesNotExist:
                raise Exception("Pos Type does not exists")

        beautician_id = kwargs.get("beautician_id")
        beautician = None
        if beautician_id:
            try:
                beautician = Beautician.objects.get(pk=beautician_id, organization=org)
            except Beautician.DoesNotExist:
                raise Exception("Beautician does not exists")

        status_id = kwargs.get("status_id")
        status = None
        if status_id:
            try:
                status = SessionStatus.objects.get(pk=status_id, organization=org)
            except SessionStatus.DoesNotExist:
                raise Exception("Status Type does not exists")

        booking_id = kwargs.get("booking_id")
        booking = None
        if booking_id:
            try:
                booking = Booking.objects.get(pk=booking_id, organization=org)
            except Booking.DoesNotExist:
                raise Exception("Booking does not exists")

        item = Session(
            open_date_time=kwargs.get("open_date_time"),
            close_date_time=kwargs.get("close_date_time"),
            pos=pos,
            beautician=beautician,
            status=status,
            booking=booking,
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonSession(ok=True, session=item)


class DeleteSalonSession(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()

        try:
            item = Session.objects.get(pk=id, organization=org)
        except Session.DoesNotExist:
            raise Exception("Session does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonSession(ok=True)


class UpdateSalonSession(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        open_date_time = graphene.DateTime()
        close_date_time = graphene.DateTime()
        pos_id = graphene.Int()
        beautician_id = graphene.Int()
        status_id = graphene.Int()
        booking_id = graphene.Int()

    ok = graphene.Boolean()
    session = graphene.Field(SessionType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Session.objects.get(pk=id, organization=org)
        except Session.DoesNotExist:
            raise Exception("Session does not exist")

        pos_id = kwargs.get("pos_id")
        pos = None
        if pos_id:
            try:
                pos = Pos.objects.get(pk=pos_id, organization=org)
            except Pos.DoesNotExist:
                raise Exception("Pos does not exists")

        beautician_id = kwargs.get("beautician_id")
        beautician = None
        if beautician_id:
            try:
                beautician = Beautician.objects.get(pk=beautician_id, organization=org)
            except Beautician.DoesNotExist:
                raise Exception("Beautician does not exists")

        status_id = kwargs.get("status_id")
        status = None
        if status_id:
            try:
                status = SessionStatus.objects.get(pk=status_id, organization=org)
            except SessionStatus.DoesNotExist:
                raise Exception("Status Type does not exists")

        booking_id = kwargs.get("booking_id")
        booking = None
        if booking_id:
            try:
                booking = Booking.objects.get(pk=booking_id, organization=org)
            except Booking.DoesNotExist:
                raise Exception("Booking does not exists")

        item.open_date_time = kwargs.get("open_date_time") or item.open_date_time
        item.close_date_time = kwargs.get("close_date_time") or item.close_date_time
        item.pos = pos or item.pos
        item.beautician = beautician or item.beautician
        item.status = status or item.status
        item.booking = booking or item.booking

        item.save()
        return UpdateSalonSession(ok=True, session=item)


class Mutation(graphene.ObjectType):
    salon_session_create = CreateSalonSession.Field()
    salon_session_update = UpdateSalonSession.Field()
    salon_session_delete = DeleteSalonSession.Field()


schema_salon_session = graphene.Schema(query=Query, mutation=Mutation)
