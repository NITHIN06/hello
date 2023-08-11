from django.http import HttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from user.models import AccessTokenBlacklist
from rest_framework.response import Response
from django.http import HttpResponse
import json

from typing import Any
from user.models import User

class CheckVerifiedUser(MiddlewareMixin):
    """Custom middleware to check user email is verified or not"""

    def __call__(self, request: HttpRequest) -> HttpResponse:

        if request.method=='POST' and request.path=='/api/login/':
            user = request.POST.get('username')
            user_exist = get_user_model().objects.filter(username=user).exists()
            if user_exist:
                user = get_user_model().objects.get(username=user)
                if not user.is_verified:
                    request.verified_user = False

                    # return HttpResponse(json.dumps(response_data), content_type="application/json")

        response = self.get_response(request)

        return response

class CheckAccessToken(MiddlewareMixin):
    """Check user access token is blacklisted or not"""

    def __call__(self, request: HttpRequest) -> HttpResponse:

        header = request.META.get('HTTP_AUTHORIZATION', None)
        if header:
            print(header)
            token = header.split()[-1]
            status = AccessTokenBlacklist.objects.filter(token=token).exists()
            if status:
                response = {"status":"failed", "message":"Token expired", "data": None, "error":{}}
                return HttpResponse(json.dumps(response), content_type="application/json")

        response = self.get_response(request)


        return response