from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import Http404
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event, Team, EventUserTable
from info.models import VerifyEndpoint

import random, string, os, qrcode, time, datetime

# Create your views here.

class EventsListView(APIView):
    def get(self, request, slug):
        visit = cache.get('visits', 0)
        visit += 1
        cache.set('visits', visit)
        user = request.user
        if user.is_anonymous:
            list = cache.get(slug)
            if list!=None:
                return Response(list, status=status.HTTP_200_OK)
        if slug=='all':
            # events_queryset_after_time = Event.objects.filter(date=datetime.date.today(), time__gte=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_after_date = Event.objects.filter(date__gt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_date = Event.objects.filter(date__lt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_time = Event.objects.filter(date=datetime.date.today(), time__lt=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_null_date = Event.objects.filter(date=None).order_by('order')
            # events_queryset_today_null_time = Event.objects.filter(date=datetime.date.today(), time=None).order_by('order')
            events_queryset = Event.objects.all().order_by('order')
        elif slug=='competitions':
            # events_queryset_after_time = Event.objects.filter(type='CP', date=datetime.date.today(), time__gte=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_after_date = Event.objects.filter(type='CP', date__gt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_date = Event.objects.filter(type='CP', date__lt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_time = Event.objects.filter(type='CP', date=datetime.date.today(), time__lt=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_null_date = Event.objects.filter(type='CP', date=None).order_by('order')
            # events_queryset_today_null_time = Event.objects.filter(type='CP', date=datetime.date.today(), time=None).order_by('order')
            events_queryset = Event.objects.filter(type='CP').order_by('order')
        elif slug=='events':
            # events_queryset_after_time = Event.objects.filter(type='EV', date=datetime.date.today(), time__gte=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_after_date = Event.objects.filter(type='EV', date__gt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_date = Event.objects.filter(type='EV', date__lt=datetime.date.today()).order_by('order', 'date', 'time')
            # events_queryset_before_time = Event.objects.filter(type='EV', date=datetime.date.today(), time__lt=datetime.datetime.now().strftime('%H:%M:%S')).order_by('order', 'date', 'time')
            # events_queryset_null_date = Event.objects.filter(type='EV', date=None).order_by('order')
            # events_queryset_today_null_time = Event.objects.filter(type='EV', date=datetime.date.today(), time=None).order_by('order')
            events_queryset = Event.objects.filter(type='EV').order_by('order')
        else:
            raise Http404
        list = []
        # for events_queryset in [events_queryset_today_null_time, events_queryset_after_time, events_queryset_after_date, events_queryset_before_date, events_queryset_before_time, events_queryset_null_date]:
        for event in events_queryset:
            data = {}
            data['id'] = event.id
            data['name'] = event.name
            data['description'] = event.description
            data['image'] = event.image_url
            data['date'] = event.date
            data['time'] = event.time
            data['venue'] = event.venue
            data['type'] = event.type
            data['intra_thapar'] = event.intra_thapar
            data['category'] = event.category
            data['domain'] = event.domain
            data['deadline'] = event.deadline
            data['is_active'] = True if event.is_active and (event.deadline is None or event.deadline>timezone.now()) else False
            if event.fees_amount==0:
                data['fees'] = 'Free'
            elif event.fees_per_member==0:
                data['fees'] = 'Rs.' + str(event.fees_amount) + '/- per registration'
            else:
                data['fees'] = 'Rs.' + str(event.fees_amount) + '/- per team + Rs.' + str(event.fees_per_member) + '/- per member'
            data['is_team_event'] = event.is_team_event
            data['min_team_size'] = event.min_team_size
            data['max_team_size'] = event.max_team_size
            data['is_registered'] = False
            data['registration_allowed'] = True
            if not user.is_anonymous:
                data['is_registered'] = user.event_registrations.filter(event=event).exists() or user.leader_team_set.filter(event=event).exists() or user.team_set.filter(event=event).exists()
                if event.intra_thapar and not user.is_thaparian:
                    data['registration_allowed'] = False
            data['rules'] = []
            rules = event.rules.all().order_by('number')
            for rule in rules:
                data['rules'].append(rule.content)
            data['prize1'] = event.prize1
            data['prize2'] = event.prize2
            list.append(data)
        if user.is_anonymous:
            cache.add(slug, list)
        return Response(list, status=status.HTTP_200_OK)

class EventView(APIView):
    def get(self, request, id):
        event = Event.objects.filter(id=id).first()
        if event is None or not event.is_active:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        data = {}
        data['id'] = event.id
        data['name'] = event.name
        data['description'] = event.description
        data['image'] = event.image_url
        data['date'] = event.date
        data['time'] = event.time
        data['venue'] = event.venue
        data['type'] = event.type
        data['intra_thapar'] = event.intra_thapar
        data['category'] = event.category
        data['domain'] = event.domain
        data['deadline'] = event.deadline
        data['is_active'] = True if event.is_active and (event.deadline is None or event.deadline>timezone.now()) else False
        if event.fees_amount==0 and event.fees_per_member==0:
            data['fees'] = 'Free'
        elif event.fees_per_member==0:
            data['fees'] = 'Rs.' + str(event.fees_amount) + '/- per registration'
        elif event.fees_amount==0:
            data['fees'] = 'Rs.' + str(event.fees_per_member) + '/- per member'
        else:
            data['fees'] = 'Rs.' + str(event.fees_amount) + '/- per team + Rs.' + str(event.fees_per_member) + '/- per member'
        data['is_team_event'] = event.is_team_event
        data['min_team_size'] = event.min_team_size
        data['max_team_size'] = event.max_team_size
        data['is_registered'] = False
        data['registration_allowed'] = True
        if not user.is_anonymous:
            data['is_registered'] = user.event_registrations.filter(event=event).exists() or user.leader_team_set.filter(event=event).exists() or user.team_set.filter(event=event).exists()
            if event.intra_thapar and not user.is_thaparian:
                data['registration_allowed'] = False
        data['rules'] = []
        rules = event.rules.all().order_by('number')
        for rule in rules:
            data['rules'].append(rule.content)
        data['prize1'] = event.prize1
        data['prize2'] = event.prize2
        return Response(data, status=status.HTTP_200_OK)

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
        if user.event_registrations.filter(event=event).exists():
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.gender=='M':
            if event.max_male_count!=None and event.curr_male_count>=event.max_male_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_male_count += 1
        elif user.gender=='F':
            if event.max_female_count!=None and event.curr_female_count>=event.max_female_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_female_count += 1
        event.save()
        regstrEntry = EventUserTable(user=user, event=event)
        if user.is_thaparian:
            regstrEntry.amount_paid = True
        regstrEntry.save()
        context = {'eventName': event.name}
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
            context['qr_url'] = url
        if not user.is_thaparian:
            context['fees_required'] = True
            context['individual_fees'] = event.fees_amount
        subject = f"Thank you for registering for {event.name}"
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
        count = request.data.get('members_count')
        if count is None:
            return Response({'error': 'Members count required.'}, status=status.HTTP_400_BAD_REQUEST)
        if count<event.min_team_size:
            return Response({'error': 'Members count should be greater than minimum team size'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if event.intra_thapar and not user.is_thaparian:
            return Response({'error': 'Not allowed. This event is for Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_thaparian and event.type=='CP' and event.category=='CL':
            return Response({'error': 'Auditions for Thapar students are over.'}, status=status.HTTP_400_BAD_REQUEST)
        is_leader = user.team_set.filter(event=event).exists()
        is_member = user.leader_team_set.filter(event=event).exists()
        if is_leader or is_member:
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.gender=='M':
            if event.max_male_count!=None and event.curr_male_count>=event.max_male_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_male_count += 1
        elif user.gender=='F':
            if event.max_female_count!=None and event.curr_female_count>=event.max_female_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_female_count += 1
        event.save()
        key = getRandomKey()
        while Team.objects.filter(key=key).exists():
            key = getRandomKey()
        team = Team(leader=user, event=event, name=name, key=key, max_count=count)
        if user.is_thaparian:
            team.amount_paid = True
        else:
            team.is_thapar_team = False
        team.save()
        context = {
            'eventName': event.name,
            'teamName': name,
            'teamKey': key
        }
        if not user.is_thaparian:
            context['fees_required'] = True
            context['team_amount'] = event.fees_amount
            context['fees_per_member'] = event.fees_per_member
            context['members_count'] = team.max_count
            context['total_fees'] = event.fees_amount + (event.fees_per_member*team.max_count)
        subject = f"Thank you for registering for {event.name}"
        html_message = render_to_string('events/mail.html', context)
        message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [user.email], html_message=html_message, fail_silently=False)
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
        if team.is_thapar_team and not user.is_thaparian:
            return Response({'error': 'Not allowed. This team is of Thapar Students only.'}, status=status.HTTP_401_UNAUTHORIZED)
        is_leader = user.team_set.filter(event=event).exists()
        is_member = user.leader_team_set.filter(event=event).exists()
        if is_leader or is_member:
            return Response({'error': 'User already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.gender=='M':
            if event.max_male_count!=None and event.curr_male_count>=event.max_male_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_male_count += 1
        elif user.gender=='F':
            if event.max_female_count!=None and event.curr_female_count>=event.max_female_count:
                return Response({'error': 'Registrations closed'}, status=status.HTTP_400_BAD_REQUEST)
            event.curr_female_count += 1
        event.save()
        key = request.data.get('key')
        if key is None:
            return Response({'error': 'Key is required.'}, status=status.HTTP_400_BAD_REQUEST)
        team = Team.objects.filter(key=key).first()
        if team is None:
            return Response({'error': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
        if team.members.count()+1==event.max_team_size or team.members.count()+1==team.max_count:
            return Response({'error': 'Team Full'}, status=status.HTTP_400_BAD_REQUEST)
        team.members.add(user)
        team.save()
        context = {
            'eventName': event.name
        }
        if not team.amount_paid:
            context['fees_message'] = True
            context['fees_required'] = True
        subject = f"Thank you for registering for {event.name}"
        html_message = render_to_string('events/mail.html', context)
        message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [user.email], html_message=html_message, fail_silently=False)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
