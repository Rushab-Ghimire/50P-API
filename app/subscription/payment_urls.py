"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from subscription.payment import payment_views, payment_chargebee_webhook_views

router = DefaultRouter()

app_name = 'subscription'

router.register("", payment_views.ChargebeeInvoiceView, basename="chargebee")
router.register("", payment_views.ChargebeePaymentSourceView, basename="chargebee")

urlpatterns = [
    path('chargebee/hosted_page/',  payment_views.ChargebeeCreateSubscriptionView.as_view(), name='chargebee-hosted-page'),
    path('chargebee/webhook/',  payment_chargebee_webhook_views.ChargebeeWebhookView.as_view(), name='chargebee-webhook'),
    path('chargebee/customer/',  payment_views.ChargebeeCustomerView.as_view(), name='chargebee-customer'),
    # path('chargebee/customer/invoices', payment_views.ChargebeeInvoiceView.as_view(), name='chargebee-customer-invoices'),
    path('', include(router.urls)),
]
