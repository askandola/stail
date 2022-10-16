from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventsView.as_view()),
    path('event/<int:id>', views.EventView.as_view()),
    path('event-register/', views.EventRegisterView.as_view()),
]
