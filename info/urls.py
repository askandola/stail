from django.urls import path

from . import views

urlpatterns = [
    path('sponsors/', views.SponsorsView.as_view()),
    path('query/', views.QueryView.as_view()), #contact us form
    path('event-registration-details/<int:id>', views.streamEventRegstCSV, name="getEventRegistrationsList")
]