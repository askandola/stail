from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.EventView.as_view()),
    path('register/', views.EventRegisterView.as_view()),
    path('create-team/', views.CreateTeam.as_view()),
    path('join-team/', views.JoinTeam.as_view()),
    path('<slug:slug>/', views.EventsListView.as_view()),
]
