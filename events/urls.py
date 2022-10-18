from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.EventsListView.as_view()),
    path('<int:id>/', views.EventView.as_view()),
    path('register/', views.EventRegisterView.as_view()),
]
