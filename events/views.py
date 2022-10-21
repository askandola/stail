from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import EventSerializer
from .models import Event, Visit
from info.models import VerifyEndpoint

import random, string, os, qrcode

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
            if event.verification_required:
                endpoint = ''.join(random.choice(string.ascii_letters) for _ in range(100))
                while VerifyEndpoint.objects.filter(endpoint=endpoint).exists():
                    endpoint = ''.join(random.choice(string.ascii_letters) for _ in range(100))
                verificationEntry = VerifyEndpoint(endpoint=endpoint, event=event, user=user)
                verificationEntry.save()
                filename = 'qrcode/' + str(event_id) + '_' + str(user.id) + '_temp.png'
                qr = qrcode.make(('https://' if request.is_secure() else 'http://') + request.META['HTTP_HOST'] + '/info/verify/' + endpoint + '/')
                qr.save(os.path.join(settings.MEDIA_ROOT, filename))
                url = ('https://' if request.is_secure() else 'http://') + request.META['HTTP_HOST'] + '/media/' + filename
                subject = "Thankyou for registering"
                context = {'url': url}
                html_message = render_to_string('events/mail.html', context)
                message = strip_tags(html_message)
                from_email = settings.EMAIL_HOST_USER
                send_mail(subject, message, from_email, [user.email], html_message=html_message, fail_silently=False)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
