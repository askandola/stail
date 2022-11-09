from rest_framework.serializers import ModelSerializer

from .models import Event

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'description', 'image', 'date', 'time', 'venue', 'type', 'intra_thapar', 'is_team_event', 'min_team_size', 'max_team_size']
