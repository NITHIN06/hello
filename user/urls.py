from django.urls import path, include

from user.v1 import views

# Define urls here
urlpatterns = [
    path('',include('user.v1.urls')),
]