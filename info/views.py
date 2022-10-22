from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import QuerySerializer, SponsorSerializer
from .models import Sponsor
from events.models import Event, Visit
from registrations.models import User

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


@staff_member_required
def DashboardView(request):
    events_queryset = Event.objects.all()
    registrations = User.objects.filter(is_staff=False).count()
    total_visits = Visit.objects.filter(event=None).first()
    if total_visits is None:
        total_visits = Visit()
        total_visits.save()
    events = []
    for event in events_queryset:
        data = {'id': event.id, 'name': event.name, 'registrations': event.users.count()}
        visit = Visit.objects.filter(event=event).first()
        if visit is not None:
            data['visits'] = visit.hits
        else:
            data['visits'] = 0
        events.append(data)
    context = {
        'events': events,
        'visits': total_visits.hits,
        'registrations': registrations,
        'eventsCount': len(events),
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
            raise 404
        users = event.users.all()
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        headGen = (writer.writerow(['ID', 'Name', 'Email ID', 'Phone Number', 'Thapar Student', 'Roll Number', 'College Name', 'ID Proof URL']) for i in range(1))
        dataGen = (writer.writerow([user.id, user.name, user.email, user.phone_no, user.is_thaparian, user.roll_no, user.college, user.id_proof]) for user in users)
        gen = itertools.chain(headGen, dataGen)
        return StreamingHttpResponse(
            gen,
            content_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="{event.name}_registrations.csv"'
            },
        )
    raise 404


class VerifyRegistrationView(APIView):
    def get(self, request, slug):
        visit = Visit.objects.filter(endpoint=slug).first()
        if visit is None:
            return Response({'error': 'Not Found'}, status=status.HTTP_400_BAD_REQUEST)
        user = visit.user
        event = visit.event
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
