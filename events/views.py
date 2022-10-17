from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event, total_views
from .serializers import EventSerializer

# Create your views here.

class EventsView(APIView):
    def get(self, request):
        if (total_views.objects.count()==0):
            t=total_views(hits=1)
            t.save()
        else:
            t=total_views.objects.first()
            t.hits+=1
            t.save()
        events_queryset = Event.objects.all()
        print(events_queryset)
        serializer = EventSerializer(events_queryset, many=True)
        return Response({'events': serializer.data}, status=status.HTTP_200_OK)

class EventView(APIView):
    def get(self, request, id):
        event_queryset = Event.objects.filter(id=id).first()
        print(event_queryset)
        if event_queryset is None:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventSerializer(event_queryset)
        data = serializer.data.copy()
        user = request.user
        if not user.is_anonymous:
            data['is_registerd'] = user.event_set.filter(id=id).exists()
            if event_queryset.intra_thapar and not user.is_thaparian:
                data['registration_allowed'] = False
            else:
                data['registration_allowed'] = True
        return Response(data, status=status.HTTP_302_FOUND)

class EventRegisterView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        event_id = request.data.get('event')
        event = Event.objects.filter(id=event_id).first()
        if event is None:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if event.intra_thapar and not user.is_thaparian:
            return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.event_set.filter(id=event_id).exists():
            event.users.add(user)
            event.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)