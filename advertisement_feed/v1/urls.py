from django.urls import path

from advertisement_feed.v1 import views

urlpatterns = [
    path('create_ad/', views.AdvertisementView.as)
]