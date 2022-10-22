from rest_framework.serializers import ModelSerializer

from .models import Event

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        exclude = ['users', 'verification_required', 'is_active']
