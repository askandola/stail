from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import EventSerializer
from .models import Event, Visit

# Create your views here.

class EventsListView(APIView):
    def get(self, request):
        visit = Visit.objects.filter(event=None).first()
        if (visit==None):
            visit = Visit(hits=1)
        else:
            visit.hits += 1
        visit.save()
        events_queryset = Event.objects.all()
        print(events_queryset)
        serializer = EventSerializer(events_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EventView(APIView):
    def get(self, request, id):
        event_queryset = Event.objects.filter(id=id).first()
        print(event_queryset)
        if event_queryset is None:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        visit = Visit.objects.filter(event=event_queryset).first()
        if visit is None:
            visit = Visit(event=event_queryset, hits=1)
        else:
            visit.hits += 1
        visit.save()
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
            return Response({'error': 'Not allowed. This event is for Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.event_set.filter(id=event_id).exists():
            event.users.add(user)
            event.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
