from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# from .serializers import UserSerializer 
from .serializers import UserSerializer, UnverifiedUserSerializer
# from .models import User, EmailVerification
from .models import User, UnverifiedUser, PendingEmail

import random, string

# Create your views here.

# class GetOTPView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         if email is None:
#             return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
#         entry = EmailVerificationOtp(email=email).first()
#         if entry is None:
#             otp = ''.join(random.choice(string.digits) for i in range(6))
#             entry = EmailVerificationOtp(email=email, otp=otp)
#             entry.save()
#         else:
#             otp = entry.otp
#         send_mail("OTP for registering.", f"Your OTP for registration is {otp}", settings.EMAIL_HOST_USER, [email,], fail_silently=False)
#         return Response({'status': 'success'}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        data = {
            'email': request.data.get('email'),
            'name': request.data.get('name'),
            'password': request.data.get('password'),
            'phone_no': request.data.get('phone_no'),
            'gender': request.data.get('gender'),
            # 'otp': request.data.get('otp'),
        }
        is_error = False
        roll_no_missing = False
        college_missing = False
        id_missing = False
        user_exists = False
        # wrong_otp = False
        if User.objects.filter(email=data['email']).exists():
            is_error = True
            user_exists = True
        is_thaparian = request.data.get('is_thaparian')
        if is_thaparian=="true" or is_thaparian==True:
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
            data['id_proof'] = id_proof
            data['college'] = college
        # otp_entry = EmailVerificationOtp.objects.filter(email=data['email']).first()
        # if otp_entry is None or data['otp']!=otp_entry.otp:
        #     is_error = True
        #     wrong_otp = True
        verification_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        while UnverifiedUser.objects.filter(slug=verification_slug).exists():
            verification_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        data['slug'] = verification_slug
        serializer = UnverifiedUserSerializer(data=data)
        # serializer = UserSerializer(data=data)
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
            if user_exists:
                errors['email'] = ['Email already exists.']
            # if wrong_otp:
            #     errors['otp'] = ['Wrong OTP.']
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        email_entry = PendingEmail(email=data['email'], slug=verification_slug, is_main=True)
        if data.get('is_thaparian', False):
            serializer.save()
        else:
            serializer = UserSerializer(data=data)
            if not serializer.is_valid():
                return Response({'error': 'OOPS! Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            user.set_password(data['password'])
            user.save()
            email_entry.main_vrf_skip = True
        # user = User.objects.filter(email=data['email']).first()
        # verification_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        # while EmailVerification.objects.filter(slug=verification_slug).exists():
        #     verification_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        # verification_entry = EmailVerification(user=user, slug=verification_slug)
        # verification_entry.save()
        # verification_url = ('https://' if request.is_secure() else 'http://') + request.META['HTTP_HOST'] + '/request7/verify/' + verification_slug
        # html_message = render_to_string('registrations/reg.html', {'verification_url': verification_url})
        # mesg = strip_tags(html_message) #incase rendering fails
        # subj = "Thank you for registering for Saturnalia'22"
        # from_email= settings.EMAIL_HOST_USER
        # send_mail(subj, mesg, from_email, [data['email'],],html_message=html_message, fail_silently=False)
        email_entry.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

# def VerifyEmail(request, slug):
#     vEntry = EmailVerification.objects.filter(slug=slug).first()
#     if vEntry is None:
#         raise Http404
#     user = vEntry.user
#     user.is_verified = True
#     user.save()
#     vEntry.delete()
#     return redirect('https://www.saturnaliatiet.com/verification', permanent=False)

def VerifyEmail(request, slug):
    vEntry = UnverifiedUser.objects.filter(slug=slug).first()
    data = UserSerializer(vEntry).data.copy()
    if vEntry is None:
        raise Http404
    serializer = UserSerializer(data=data)
    if not serializer.is_valid():
        raise Http404
    serializer.save()
    vEntry.delete()
    return redirect('https://www.saturnaliatiet.com/verification', permanent=False)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if UnverifiedUser.objects.filter(email=email).exists():
            return Response({'error': 'Email unverified.'}, status=status.HTTP_401_UNAUTHORIZED)
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        data = {
            'name': user.name,
            'key': token.key,
        }
        return Response(data, status=status.HTTP_200_OK)

class reset_request(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        user = User.objects.filter(email=email).first()
        if user is not None:
            # send email with otp
            otp = ''.join(random.choice(string.digits) for _ in range(7))
            user.otp = otp
            user.save()
            html_message = render_to_string('registrations/otp.html', {'otp': otp})
            message = strip_tags(html_message) #incase rendering fails
            subj = "Password Reset OTP for Saturnalia'22"
            from_email= settings.EMAIL_HOST_USER
            send_mail(subj, message, from_email, [data['email'],],html_message=html_message, fail_silently=False)
            message = {
                'status': 'Success'}
            return Response(message, status=status.HTTP_200_OK)
        else:
            message = {
                'error': "User doesn't exist"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

class reset_password(APIView):
    def post(self, request):
        data = request.data
        user = User.objects.filter(email=data.get('email')).first()
        if user is not None:
            # Check if otp is valid
            if data.get('otp') == user.otp:
                if data.get('password') != None and data.get('password') != '':
                    # Change Password
                    user.set_password(data['password'])
                    user.otp = None
                    user.save()
                    return Response({'status': 'success'}, status.HTTP_200_OK)
                else:
                    message = {
                        'error': "Password can't be empty"}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                message = {
                    'error': 'OTP did not match'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = {
                'error': "User doesn't exist."}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
