from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer

# Create your views here.

class Register(APIView):
    def post(self, request):
        data = {
            'email': request.data.get('email'),
            'name': request.data.get('name'),
            'id_proof': request.data.get('id_proof'),
            'password': request.data.get('password'),
        }
        is_error = False
        roll_no_missing = False
        college_missing = False
        is_thaparian = request.data.get('is_thaparian')
        if is_thaparian==True:
            roll_no = request.data.get('roll_no')
            if roll_no is None:
                roll_no_missing = True
                is_error = True
            data['is_thaparian'] = True
            data['roll_no'] = roll_no
        else:
            college = request.data.get('college')
            if college is None:
                college_missing = True
                is_error = True
            data['college'] = college
        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            is_error = True
        if is_error:
            errors = serializer.errors.copy()
            if roll_no_missing:
                if errors.get('roll_no') is None:
                    errors['roll_no'] = ['Roll Number required.']
                else:
                    errors['roll_no'].append("Roll number required.")
            if college_missing:
                if errors.get('college') is None:
                    errors['college'] = ['College name required']
                else:
                    errors['college'].append("College name required.")
            return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'key': token.key}, status=status.HTTP_200_OK)
