"""
URL mappings for the user API.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from authtf import views

from .views import (
    CustomerViewSet
)

router = DefaultRouter()

router.register('customer', CustomerViewSet)

app_name = 'authtf'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('set-invited-user-password/<str:token>/', views.SetInvitedUserPasswordView.as_view(), name='set-invited-user-password'),
    path('verify-new-user/', views.VerifyNewUserView.as_view(), name='verify-new-user'),
    path('reset-password-request/', views.ResetPasswordRequestView.as_view(), name='password-reset-request'),
    path('verify-reset-password-request/<str:token>/', views.VerifyResetPasswordRequestView.as_view(), name='verify-password-reset-request'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]
