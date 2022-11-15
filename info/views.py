from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import QuerySerializer, SponsorSerializer
from .models import Sponsor, VerifyEndpoint
from events.models import Event
from registrations.models import User, UnverifiedUser
from .models import Query, Visit

import csv, itertools

# Create your views here.

#for contact us form
class QueryView(APIView):
    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SponsorsView(APIView):
    def get(self, request):
        queryset = Sponsor.objects.all()
        serializer = SponsorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def update_db_from_cache():
    db_entry = Visit.objects.first()
    if db_entry==None:
        db_entry = Visit()
    cache_entry = cache.get('visits', 0)
    db_entry.hits += cache_entry
    cache.set('visits', 0)
    db_entry.save()


@staff_member_required
def DashboardView(request):
    update_db_from_cache()
    events_queryset = Event.objects.all()
    # registrations = User.objects.filter(is_staff=False, is_verified=True).count()
    registrations = User.objects.filter(is_staff=False).count()
    # pending_verifications = EmailVerification.objects.count()
    pending_verifications = UnverifiedUser.objects.count()
    total_visits = Visit.objects.first()
    unread_queries = Query.objects.filter(is_read=False).count()
    if total_visits is None:
        total_visits = Visit()
        total_visits.save()
    events = []
    for event in events_queryset:
        data = {'id': event.id, 'name': event.name, 'registrations': event.teams.count() if event.is_team_event else event.users.count()}
        events.append(data)
    context = {
        'events': events,
        'visits': total_visits.hits,
        'registrations': registrations,
        'eventsCount': len(events),
        'pendingVerification': pending_verifications,
        'unreadQueries': unread_queries,
    }
    return render(request, 'info/dashboard.html', context=context)


class Echo(StreamingHttpResponse):
    def write(self, value):
        return value

@staff_member_required
def streamEventRegstCSV(request, id):
    if request.method=='POST':
        event = Event.objects.filter(id=id).first()
        if event is None:
            raise Http404
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        if event.is_team_event:
            teams = event.teams.all()
            gen = (writer.writerow(['Team ID', 'Team Name', 'User ID', 'Name', 'Email ID', 'Phone Number', 'Thapar Student', 'Roll Number', 'College Name', 'ID Proof URL']) for i in range(1))
            for team in teams:
                leadergen = (writer.writerow([team.id, team.name, team.leader.id, team.leader.name, team.leader.email, team.leader.phone_no, team.leader.is_thaparian, team.leader.roll_no, team.leader.college, team.leader.id_proof]) for i in range(1))
                members = team.members.all()
                membersgen = (writer.writerow([team.id, team.name, user.id, user.name, user.email, user.phone_no, user.is_thaparian, user.roll_no, user.college, user.id_proof]) for user in members)
                gen = itertools.chain(gen, leadergen, membersgen)
        else:
            users = event.users.all()
            headGen = (writer.writerow(['ID', 'Name', 'Email ID', 'Phone Number', 'Thapar Student', 'Roll Number', 'College Name', 'ID Proof URL']) for i in range(1))
            dataGen = (writer.writerow([user.user.id, user.user.name, user.user.email, user.user.phone_no, user.user.is_thaparian, user.user.roll_no, user.user.college, user.user.id_proof]) for user in users)
            gen = itertools.chain(headGen, dataGen)
        return StreamingHttpResponse(
            gen,
            content_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="{event.name}_registrations.csv"'
            },
        )
    raise Http404


class VerifyRegistrationView(APIView):
    def get(self, request, slug):
        entry = VerifyEndpoint.objects.filter(endpoint=slug).first()
        if entry is None:
            return Response({'error': 'Not Found'}, status=status.HTTP_400_BAD_REQUEST)
        user = entry.user
        event = entry.event
        response = {
            'event': event.name,
            'email': user.email,
            'name': user.name,
        }
        if user.is_thaparian:
            response['is_thaparian'] = True
            response['roll_no'] = user.roll_no
        else:
            response['college'] = user.college
            response['id_proof'] = user.id_proof
        return Response(response, status.HTTP_200_OK)
