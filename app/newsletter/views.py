from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response


from newsletter.models import (
    Subscriber,
    NewsletterSubscriptionSerializer,
)

class NewsletterSubscriptionView(generics.CreateAPIView):
    serializer_class = NewsletterSubscriptionSerializer


class NewsletterSubscriberCountView(APIView):
    def get(self, request):
        totalSubscribers = Subscriber.objects.all().count()
        return Response({'count': totalSubscribers}, status=status.HTTP_200_OK)
