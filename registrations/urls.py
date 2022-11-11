from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('api-key/', views.LoginView.as_view(), name='login'),
    path('reset-request/', views.reset_request.as_view()),
    path('reset-password/', views.reset_password.as_view()),
]
