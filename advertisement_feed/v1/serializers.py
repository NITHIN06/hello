from rest_framework import serializers

from advertisement_feed import models

class AdvertisementSerialiser(serializers.ModelSerializer):
    class Meta:
        model = models.Advertisement
        fields = '__all__'
        # read_only_fields = (status', 'purchased_at', 'is_agent', 'price', 'negotiable', 'featured', 'seller_name', 'contact_email', 'contact_phone')
        read_only_fields = ('user', 'is_archive', 'latitude', 'longitude', 'purchased_user_id')
    
    def save(self, *args, **kwargs):
        print(super().title)
        super().save(*args, **kwargs)