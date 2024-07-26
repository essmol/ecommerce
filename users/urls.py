
from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.views import LogoutView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
    
)

from .views import RegistertionView, UserLoginView,ActivationView, SendResendView

app_name='users'

urlpatterns = [
    
    path('register/', RegistertionView.as_view(), name='registeration'),
    path('user/token', TokenObtainPairView.as_view(), name='get-token'),
    path('user/refresh-token', TokenRefreshView.as_view(), name='refresh-token'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('activation/',ActivationView.as_view(), name='activation'),
    path('send-code/', SendResendView.as_view(), name='send-code')
    # path('login-phone-number/', ),
    # path('login-email/'),
    # path(''),
    # path('profile/')


]
