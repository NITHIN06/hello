
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.baseResponse import BaseResponse
from utils.sendEmail import send_verification_email
from . import serializers
from user import models
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str 
from rest_framework import status
from django.shortcuts import render
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework.permissions import IsAuthenticated, AllowAny
from user.tokens import email_verification_token


class UserView(APIView, BaseResponse):
    """APIView to create users"""
    serializer_class = serializers.UserModelSerializer
    
    def post(self, request):
        messages = None
        status = "failed"
        data = []
        user_serialiser = self.serializer_class(data=request.data)
        if user_serialiser.is_valid():
            status = "success"
            user = user_serialiser.save()
            subject = "Activate Your Account"
            messages = "Account registration successful. Please verify the email id by clicking the below link."
            domain = get_current_site(request).domain
            send_verification_email(user, subject, messages, domain=domain)
            user_serialiser.validated_data.pop('password')
            data = user_serialiser.validated_data
        else:
            messages = "Account registration failed"
        response = self.get_response(status=status, messages=messages, data=data, error_list=user_serialiser.errors)
        return Response(response)
        
    # def get(self, request, pk=None):
    #     if pk:
    #         user = models.User.objects.get(pk=pk)
    #         user_data = self.serializer_class(user)
    #         return Response(user_data.data)
        
    #     users = models.User.objects.all()
    #     user_data = self.serializer_class(users, many=True)
    #     return Response({"data":user_data.data})    
    
class RestoreView(APIView, BaseResponse):
    serializer_class = serializers.ResendEmailSerializer
    authentication_classes = []
    # permission_classes = [AllowAny]

    def post(self, request):
        status="success"
        message=None
        data = self.serializer_class(data=request.data)
        if data.is_valid():
            email = data.validated_data['email']
            try:
                user = models.User.all_objects.get(email=email)
                if user.deleted_at is not None:
                    message="Active account found with given email id"
                else:
                    user.restore()
                    user.save()
            except Exception as e:
                status="failed"
                message="No user found with given email id"
        response = self.get_response(status, data.validated_data, message, data.errors)
        return Response(response)

    
class LoginView(TokenObtainPairView, BaseResponse):
    serializer_class = serializers.MyTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        print(get_current_site(request))
        status = "failed"
        messages = None
        data = []

        if hasattr(request, 'verified_user'):
            messages = "Email not verified"
            response = self.get_response(status=status, data=data, messages=messages, error_list=[])
            return Response(response)


        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid():
            status="success"
            messages = "User login successful"
            data = serializer_data.validated_data
        else:
            messages = "Invalid credentials"
        response = self.get_response(status=status, data=data, messages=messages, error_list=serializer_data.errors)
        return Response(response)


class RefreshTokenView(TokenRefreshView, BaseResponse):
    serializer_class = serializers.MyTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        status = "failed"
        messages = None
        data = []

        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid():
            status="success"
            messages = "Token refresh successful"
            data = serializer_data.validated_data
        response = self.get_response(status=status, data=data, messages=messages, error_list=serializer_data.errors)
        return Response(response)


class VerifyView(APIView):
    def get_user_from_email_verification_token(self, uidb64, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
        
        except (TypeError, ValueError, OverflowError, models.User.DoesNotExist) as e:
            return None
        print(email_verification_token.check_token(user, token))
        if user is not None and email_verification_token.check_token(user, token):
            return user

        return None

    def get(self, request, uidb64, token):
        message=""
        status=""
        user = self.get_user_from_email_verification_token(uidb64, token)
        if user:
            if user.is_verified:
                status = " Already Verified"
                message = "Your email has already been verified. You can access all the features of our website."
            else:
                user.is_verified = True
                user.save()
                status = "Email Verified"
                message = "Your email has been successfully verified. You can now access all the features of our website."
        else:
            status="Email Verification Failed"
            message="Invalid varification link. Verification link expired or invalid"
        context = {
                'user': user if user else "",
                "status": status,
                "message":message,
                'link': reverse('User Login'),
                'site_label': 'Login'
            }
        return render(request, 'email_verified.html', context)


class ProfileApiView(APIView):
    serializers_class = serializers.ProfileSerialiser
    def get(self, request, pk=None):
        if pk==None:
            data = models.Profile.objects.all()
            serializer = self.serializers_class(data)
            return Response(data=serializer.data)
        
        data = models.Profile.objects.select_related('user').get(pk=pk)
        serializer = self.serializers_class(data)
        return Response(serializer.data)

class UserProfileApiView(APIView, BaseResponse):
    """APIView to View, and Update"""
    serializer_class = serializers.UserProfileSerialiser
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """Get request to details (user and profile fields)"""

        user = models.User.objects.get(username=request.user)
        serialiser = self.serializer_class(user)
        response = self.get_response(status="success", data=serialiser.data, error_list={})
        return Response(response)
          

    def put(self, request):
        """Update request to details (user and profile fields)"""
        status = "failed"
        obj = models.User.objects.get(pk=request.user.id)
        details = self.serializer_class(obj, data=request.data, partial=True)
        message=None

        if details.is_valid():
            # access_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[-1]
            details.save()
            message = "User details updated successfully"
            if "email" in details.validated_data:
                message+=". Please check the inbox to verify the new email Id."
            status = "success"

        response = self.get_response(status=status, messages=message, data=details.validated_data, error_list=details.errors)
        return Response(response)
    
    def delete(self, request):
        obj = models.User.objects.get(pk=request.user.id)
        refresh = request.data["refresh"]
        token = RefreshToken(refresh)
        token.blacklist()
        obj.soft_delete()
        response = self.get_response(status="success", messages="Account deletion success")
        return Response(response)


class LogoutView(APIView, BaseResponse):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        status = "failed"
        messages = None
        errors_list = {}
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)

            token.blacklist()
            status="success"
            messages = "Logout successfull"

        except Exception as e:
            messages = "User logged out already"
            errors_list["token"] = [str(e)]

        response = self.get_response(status=status, messages=messages, data=[], error_list=errors_list)
        return Response(response)   

class UpdatePasswordView(APIView, BaseResponse):
    serializer_class = serializers.UpdatePassword
    permission_classes = [IsAuthenticated]

    def put(self, request):
        messages = None
        status = "failed"

        obj = models.User.objects.get(pk=request.user.id)
        details = self.serializer_class(obj, data=request.data, context={'request': request})

        if details.is_valid():
            status = "success"
            details.save()
            messages = "Password updated successfully"
        
        response = self.get_response(status=status, data = [], messages=messages, error_list=details.errors)
        return Response(response)

class ResendEmailView(APIView, BaseResponse):
    serializer_class = serializers.ResendEmailSerializer

    def post(self, request):
        status = 'success'
        message_r = None # api response
        data = self.serializer_class(data=request.data)
        if data.is_valid():
            try:
                email = data.validated_data['email']
                user = models.User.objects.get(email=email)
                subject = "Activate Your Account: Resent Verification Link"
                message = "Requested to resend verification link. Please click on the below link to verify your email id"
                domain = get_current_site(request).domain
                send_verification_email(user, subject, message, domain=domain)
            except Exception as e:
                status = 'failed'
                message_r = "No user records found with the matching email id"
        else:
            status = 'failed'
        
        response = self.get_response(status=status, data=data.validated_data, messages=message_r, error_list=data.errors)
        return Response(response)

class PasswordResetView(APIView, BaseResponse):
    serializer_class = serializers.ResendEmailSerializer

    def post(self, request):
        status = 'success'
        message_r = None # api response
        data = self.serializer_class(data=request.data)
        if data.is_valid():
            try:
                email = data.validated_data['email']
                user = models.User.objects.get(email=email)
                subject = "Reset Password Request"
                message = "Reset your password by clicking the below link."
                domain = get_current_site(request).domain
                token_generator = PasswordResetTokenGenerator()
                send_verification_email(user, subject, message, domain=domain, token_generator=token_generator)
            except Exception as e:
                status = 'failed'
                message_r = "No user records found with the matching email id"
        else:
            status = 'failed'
        
        response = self.get_response(status=status, data=data.validated_data, messages=message_r, error_list=data.errors)
        return Response(response)
    
class VerifyPasswordResetLink(APIView, BaseResponse):
    serializer_class = serializers.VerifyPasswordResetSerializer
    token_generator = PasswordResetTokenGenerator()

    def get_user_from_password_reset_token(self, uidb64, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
            print(user)
        except (TypeError, ValueError, OverflowError, models.User.DoesNotExist) as e:
            return None
        print(self.token_generator.check_token(user, token))
        if user is not None and self.token_generator.check_token(user, token):
            return user

        return None
    
    def put(self, request, uidb64, token):
        message=None
        status=""

        user = self.get_user_from_password_reset_token(uidb64, token)
        print(user)
        if user:
            data = self.serializer_class(user, data=request.data)
            if data.is_valid():
                data.save()
                status = "Password update successful"
                message = "Your password has been updated successfully. You can login with your new password."
            else:
                status = "Password reset failed"
                message = f"Password update failed.\n{data.errors}"
        else:
            status="Password reset failed"
            message="Invalid link. Link expired or invalid"
        context = {
                'user': user if user else "",
                "status": status,
                "message":message,
                'link': reverse('User Login'),
                'site_label': 'Login'
            }
        return render(request, 'email_verified.html', context)


# class UserProfileCreation(APIView):
#     """User creation along with profile details"""
#     serializer_class = serializers.UserProfileSerialiser
#     def put(self, request, pk):
#         user_obj = models.User.objects.get(pk=pk)
#         profile_obj = models.Profile.objects.get(user=user_obj)

#         userserialiser = serializers.UserModelSerializer(user_obj, data=request.data)
#         profileserialiser = serializers.ProfileSerialiser(profile_obj, data=request.data)

#         userserialiser.is_valid()
#         profileserialiser.is_valid()

#         if userserialiser.is_valid() and profileserialiser.is_valid():
#             userserialiser.save()
#             profileserialiser.update()
#             return Response({"message":"User detail updated successfully"})
#         else:
#             errors = {}
#             errors.update(userserialiser.errors)
#             errors.update(profileserialiser.errors)

#             return Response(
#                 {"message": "User and/or Profile update failed.", "errors": errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )