from rest_framework.views import APIView
from rest_framework.response import Response

from advertisement_feed.v1 import serializers


class AdvertisementView(APIView):
    serializer_classes = serializers.AdvertisementSerialiser

    def post(self, request):
        data = self.serializer_classes(data=request.data)
        if data.is_valid():
            data.save()
        return Response({"message":"Saved successfully"})
    