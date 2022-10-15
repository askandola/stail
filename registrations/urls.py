from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('api-key/', views.Login.as_view(), name='login'),
]
