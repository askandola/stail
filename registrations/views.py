from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.files.storage import default_storage

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from .models import User

import pyrebase, random, string, os
from decouple import config

# Create your views here.

firebaseConfig = {
    "apiKey": config("apiKey"),
    "authDomain": config("authDomain"),
    "projectId": config("projectId"),
    "storageBucket": config("storageBucket"),
    "messagingSenderId": config("messagingSenderId"),
    "appId": config("appId"),
    "measurementId": config("measurementId"),
    "databaseURL": config("databaseURL")
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
auth = firebase.auth()

user = auth.sign_in_with_email_and_password(config('firebaseAuthEmail'), config('firebaseAuthPassword'))

allowed_ext = ['.pdf', '.png', '.jpg', '.jpeg']

class RegisterView(APIView):
    def post(self, request):
        data = {
            'email': request.data.get('email'),
            'name': request.data.get('name'),
            'password': request.data.get('password'),
            'phone_no': request.data.get('phone_no'),
        }
        is_error = False
        roll_no_missing = False
        college_missing = False
        id_missing = False
        invalid_file = False
        oversize_file = False
        save_id = False
        is_thaparian = request.data.get('is_thaparian')
        if is_thaparian=="true":
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
            id_proof = request.data.get('id_proof')
            if id_proof is None:
                id_missing = True
                is_error = True
            else:
                ext = os.path.splitext(id_proof.name)
                ext = ext[1]
                if ext not in allowed_ext:
                    invalid_file = True
                    is_error = True
                elif id_proof.size>512000:
                    oversize_file = True
                    is_error = True
                save_id = True
            data['college'] = college
        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            is_error = True
        if is_error:
            errors = serializer.errors.copy()
            if roll_no_missing:
                errors['roll_no'] = ['Roll Number required.']
            if college_missing:
                errors['college'] = ['College name required']
            if id_missing:
                errors['id_proof'] = ['ID proof required']
            elif invalid_file:
                errors['id_proof'] = ['Invalid file type.']
            elif oversize_file:
                errors['id_proof'] = ['File size limit exceeded.']
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        if save_id:
            file = request.data.get('id_proof')
            filename = ''.join(random.choice(string.ascii_letters) for _ in range(10)) + '_' + file.name
            sysFilename = default_storage.save('id_proof/'+filename, file)
            storage.child('id/'+filename).put('media/'+sysFilename)
            url = storage.child('id/'+filename).get_url(user['idToken'])
            sys_delete = default_storage.delete(sysFilename)
            data['id_proof_url'] = url
            serializer = UserSerializer(data=data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'key': token.key}, status=status.HTTP_200_OK)

# class reset_request(APIView):
#     def post(self, request):
#         data = request.data
#         email = data['email']
#         user = User.objects.get(email=email)
#         if User.objects.filter(email=email).exists():
#             # send email with otp
#             send_mail(
#             'OTP for password reset',
#             f'The OTP to change your password is {user.otp}. Do not share this with anyone.',
#             'from@example.com',
#             [user.email],
#             fail_silently=False,
#             )
#             message = {
#                 'status': 'Success'}
#             return Response(message, status=status.HTTP_200_OK)
#         else:
#             message = {
#                 'error': 'User does not exist'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
# class reset_password(APIView):
#     def post(self, request):
#         data = request.data
#         user = User.objects.get(email=data.get('email'))
#         if user is not None:
#             if user.tries<5:
#                 # Check if otp is valid
#                 if data['otp'] == user.otp:
#                     if data['password'] != '':
#                         # Change Password
#                         user.set_password(data['password'])
#                         user.save() # Here user otp will also be changed on save automatically 
#                         return Response('any response or you can add useful information with response as well. ')
#                     else:
#                         message = {
#                             'error': 'Password cant be empty'}
#                         return Response(message, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     user.tries += 1
#                     message = {
#                         'error': 'OTP did not match','tries_left': 5-user.tries}
#                     return Response(message, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 message={
#                     'error': 'You have exceeded the number of tries. Request password change again for new OTP'}
#                 user.tries = 0
#                 user.save()
#                 return Response(message, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             message = {
#                 'error': 'User doesn't exist.'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)