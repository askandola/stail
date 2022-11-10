from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import EventSerializer
from .models import Event, Visit, Team
from info.models import VerifyEndpoint

import random, string, os, qrcode, time

# Create your views here.

class EventsListView(APIView):
    def get(self, request, slug):
        visit = Visit.objects.filter(event=None).first()
        if (visit==None):
            visit = Visit(hits=1)
        else:
            visit.hits += 1
        visit.save()
        if slug=='all':
            events_queryset = Event.objects.all()
        elif slug=='competitions':
            events_queryset = Event.objects.filter(type='CP')
        elif slug=='events':
            events_queryset = Event.objects.filter(type='EV')
        else:
            raise Http404
        user = request.user
        list = []
        for event in events_queryset:
            data = {}
            data['id'] = event.id
            data['name'] = event.name
            data['description'] = event.description
            if event.image_required:
                image_url = "https://" if request.is_secure() else 'http://' + request.META['HTTP_HOST'] + '/media/' + str(event.image)
                data['image'] = image_url
            else:
                data['image'] = None
            data['date'] = event.date
            data['time'] = event.time
            data['venue'] = event.venue
            data['type'] = event.type
            data['intra_thapar'] = event.intra_thapar
            data['deadline'] = event.deadline
            data['is_active'] = True if event.is_active and (event.deadline is None or event.deadline>timezone.now()) else False
            data['fees_amount'] = event.fees_amount
            data['is_team_event'] = event.is_team_event
            data['min_team_size'] = event.min_team_size
            data['max_team_size'] = event.max_team_size
            data['is_registered'] = False
            data['registration_allowed'] = True
            if not user.is_anonymous:
                data['is_registered'] = user.event_set.filter(id=event.id).exists()
                if event.intra_thapar and not user.is_thaparian:
                    data['registration_allowed'] = False
            data['rules'] = []
            rules = event.rules.order_by('number').all()
            for rule in rules:
                data['rules'].append(rule.content)
            list.append(data)
        return Response(list, status=status.HTTP_200_OK)

class EventView(APIView):
    def get(self, request, id):
        event = Event.objects.filter(id=id).first()
        if event is None or not event.is_active:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        visit = Visit.objects.filter(event=event).first()
        if visit is None:
            visit = Visit(event=event, hits=1)
        else:
            visit.hits += 1
        visit.save()
        user = request.user
        data = {}
        data['id'] = event.id
        data['name'] = event.name
        data['description'] = event.description
        if event.image_required==True:
            image_url = "https://" if request.is_secure() else 'http://' + request.META['HTTP_HOST'] + '/media/' + str(event.image)
            data['image'] = image_url
        else:
            data['image'] = None
        data['date'] = event.date
        data['time'] = event.time
        data['venue'] = event.venue
        data['type'] = event.type
        data['intra_thapar'] = event.intra_thapar
        data['deadline'] = event.deadline
        data['is_active'] = True if event.is_active and (event.deadline is None or event.deadline>timezone.now()) else False
        data['fees_amount'] = event.fees_amount
        data['is_team_event'] = event.is_team_event
        data['min_team_size'] = event.min_team_size
        data['max_team_size'] = event.max_team_size
        data['is_registered'] = False
        data['registration_allowed'] = True
        if not user.is_anonymous:
            data['is_registered'] = user.event_set.filter(id=id).exists()
            if event.intra_thapar and not user.is_thaparian:
                data['registration_allowed'] = False
        data['rules'] = []
        rules = event.rules.order_by('number').all()
        for rule in rules:
            data['rules'].append(rule.content)
        return Response(data, status=status.HTTP_302_FOUND)

class EventRegisterView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        event_id = request.data.get('event')
        event = Event.objects.filter(id=event_id).first()
        if event is None:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not event.is_active or (event.deadline!=None and event.deadline<timezone.now()):
            return Response({'error': 'Registrations closed.'}, status=status.HTTP_401_UNAUTHORIZED)
        if event.is_team_event:
            return Response({'error': 'Team Event.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if event.intra_thapar and not user.is_thaparian:
            return Response({'error': 'Not allowed. This event is for Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        if user.event_set.filter(id=event_id).exists():
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_verified:
            return Response({'error': 'Email unverified.'}, status=status.HTTP_401_UNAUTHORIZED)
        event.users.add(user)
        event.save()
        if event.verification_required:
            endpoint = ''.join(random.choice(string.ascii_letters) for _ in range(100))
            while VerifyEndpoint.objects.filter(endpoint=endpoint).exists():
                endpoint = ''.join(random.choice(string.ascii_letters) for _ in range(100))
            filename = 'qrcode/' + ''.join(random.choice(string.ascii_letters) for _ in range(5)) + str(event_id) + 'u' + str(user.id) + '.png'
            qr = qrcode.make(('https://' if request.is_secure() else 'http://') + request.META['HTTP_HOST'] + '/info/verify/' + endpoint)
            qr.save(os.path.join(settings.MEDIA_ROOT, filename))
            url = ('https://' if request.is_secure() else 'http://') + request.META['HTTP_HOST'] + '/media/' + filename
            verificationEntry = VerifyEndpoint(endpoint=endpoint, event=event, user=user, url=url)
            verificationEntry.save()
            subject = "Thankyou for registering"
            context = {'url': url}
            html_message = render_to_string('events/mail.html', context)
            message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [user.email], html_message=html_message, fail_silently=False)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

def getRandomKey():
    key = ''.join(random.choice(string.ascii_letters) for _ in range(6))
    key += str(int(time.time()*100000%100000))
    return key

class CreateTeam(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request):
        event_id = request.data.get('event')
        event = Event.objects.filter(id=event_id).first()
        if event is None:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not event.is_team_event:
            return Response({'error': 'Not a team event.'}, status=status.HTTP_400_BAD_REQUEST)
        if not event.is_active or (event.deadline!=None and event.deadline<timezone.now()):
            return Response({'error': 'Registrations closed.'}, status=status.HTTP_401_UNAUTHORIZED)
        name = request.data.get('name')
        if name is None:
            return Response({'error': 'Team Name required.'}, status=status.HTTP_400_BAD_REQUEST)
        if event.teams.filter(name=name).exists():
            return Response({'error': 'Team name already taken.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if event.intra_thapar and not user.is_thaparian:
            return Response({'error': 'Not allowed. This event is for Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        is_leader = user.team_set.filter(event=event).exists()
        is_member = user.leader_team_set.filter(event=event).exists()
        if is_leader or is_member:
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        key = getRandomKey()
        while Team.objects.filter(key=key).exists():
            key = getRandomKey()
        team = Team(leader=user, event=event, name=name, key=key)
        team.save()
        return Response({'key': key, 'name': name}, status=status.HTTP_201_CREATED)

class JoinTeam(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request):
        event_id = request.data.get('event')
        event = Event.objects.filter(id=event_id).first()
        if event is None:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        if not event.is_team_event:
            return Response({'error': 'Not a team event.'}, status=status.HTTP_400_BAD_REQUEST)
        if not event.is_active or (event.deadline!=None and event.deadline<timezone.now()):
            return Response({'error': 'Registrations closed.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if event.intra_thapar and not user.is_thaparian:
            return Response({'error': 'Not allowed. This event is for Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        is_leader = user.team_set.filter(event=event).exists()
        is_member = user.leader_team_set.filter(event=event).exists()
        if is_leader or is_member:
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        key = request.data.get('key')
        if key is None:
            return Response({'error': 'Key is required.'}, status=status.HTTP_400_BAD_REQUEST)
        team = Team.objects.filter(key=key).first()
        if team is None:
            return Response({'error': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
        if team.members.count()+1==event.max_team_size:
            return Response({'error': 'Team Full'}, status=status.HTTP_400_BAD_REQUEST)
        team.members.add(user)
        team.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)