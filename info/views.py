from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import QuerySerializer, SponsorSerializer
from .models import Sponsor

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
