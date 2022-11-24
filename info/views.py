from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
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
    nonThaparRegistrations = User.objects.filter(is_staff=False, is_thaparian=False).count()
    # pending_verifications = EmailVerification.objects.count()
    pending_verifications = UnverifiedUser.objects.count()
    total_visits = Visit.objects.first()
    # unread_queries = Query.objects.filter(is_read=False).count()
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
        'nonThaparRegistrations': nonThaparRegistrations,
        # 'unreadQueries': unread_queries,
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
            rows = [['Team ID', 'Team Name', 'User ID', 'Name', 'Email ID', 'Phone Number', 'Thapar Student', 'Roll Number', 'College Name', 'ID Proof URL', 'Fees Paid']]
            for team in teams:
                rows.append([team.id, team.name, team.leader.id, team.leader.name, team.leader.email, team.leader.phone_no, team.leader.is_thaparian, team.leader.roll_no, team.leader.college, team.leader.id_proof, team.amount_paid])
                members = team.members.all()
                for user in members:
                    rows.append([team.id, team.name, user.id, user.name, user.email, user.phone_no, user.is_thaparian, user.roll_no, user.college, user.id_proof, team.amount_paid])
        else:
            entries = event.users.all()
            rows = [['ID', 'Name', 'Email ID', 'Phone Number', 'Thapar Student', 'Roll Number', 'College Name', 'ID Proof URL', 'Fees Paid']]
            for entry in entries:
                rows.append([entry.user.id, entry.user.name, entry.user.email, entry.user.phone_no, entry.user.is_thaparian, entry.user.roll_no, entry.user.college, entry.user.id_proof, entry.amount_paid])
        return StreamingHttpResponse(
            (writer.writerow(row) for row in rows),
            content_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="{event.name}_registrations.csv"'
            },
        )
    raise Http404


@staff_member_required
def streamOutsideEventRegstCSV(request):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    events = Event.objects.all()
    rows = [['College', 'Event', 'Team Size', 'Fee amount required', 'Fee status', 'Team name', 'Leader name', 'Phone', 'Email', 'Amount Paid', 'Screenshot Link']]
    for event in events:
        rows.append(['','','','','','','','','','',''])
        if event.is_team_event:
            teams = event.teams.filter(is_thapar_team=False).all()
            for team in teams:
                rows.append([team.leader.college, event.name, team.max_count, event.fees_amount+(event.fees_per_member*team.max_count), team.amount_paid, team.name, team.leader.name, team.leader.phone_no, team.leader.email, team.paid_amount_value, team.screenshot_link])
        else:
            entries = event.users.filter(user__is_thaparian=False).all()
            for entry in entries:
                rows.append([entry.user.college, event.name, 1, event.fees_amount, entry.amount_paid, entry.user.name, entry.user.name, entry.user.phone_no, entry.user.email, entry.paid_amount_value, entry.screenshot_link])
    return StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv",
        headers={
            'Content-Disposition': f'attachment; filename="outside_thapar_registrations.csv"'
        },
    )


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
