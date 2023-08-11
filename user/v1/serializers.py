from user import models
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, exceptions
from django.db import models as mod
from utils.passwordValidator import validate_password
from utils.baseResponse import BaseResponse

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

class UserModelSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'name', 'email', 'username', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type':'password'}
            }

        }
    def create(self, validated_data):
        user = models.User.objects.create_user(
            name = validated_data['name'],
            email = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password']
        )
        
        return user
    
    def validate_password(self, password):
        """Password validator"""
        return validate_password(password)
    

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        models.Profile.objects.create(user=user)
        print(user)
        return user
    

class ProfileSerialiser(ModelSerializer):
    # user = UserModelSerializer()
    # img_location = serializers.ImageField(validators=[validate_image])

    class Meta:
        model=models.Profile
        fields = ('id', 'phone', 'address', 'img_location')

    def create(self, validated_data):
        profile = models.User.objects.create(
            phone = validated_data['phone'],
            address = validated_data['address'],
            img_location = validated_data['image']
        )
        
        return profile
    def validate_image(self, value):
        print("--------------------------------------------hello")
        if value:
            print(value,end='\n\n\n\n')
            file_extention = value.name.split('.')[-1]
            if file_extention.lower() not in ['png', 'jpg', 'jpeg']:
                raise serializers.ValidationError('File format not supported')
        return value
    


class UserProfileSerialiser(ModelSerializer):
    """Serialiser to handle User and Profile combinedly to update and view """
    profile = ProfileSerialiser()

    class Meta:
        model = models.User
        fields = ('id', 'username', 'email', 'name', 'profile')
        read_only_fields = ('username','user')
    
    def update(self, instance, validated_data):
        """Update Profile details (fields in User model + fields in Profile model)"""
        
        if "email" in validated_data:
            instance.is_verified = False

        if "profile" in validated_data:
            print("-------------------------------here")
            profile_data = validated_data.pop('profile')
            profile = instance.profile
            profile.phone = profile_data.get('phone', profile.phone)
            profile.address = profile_data.get('address', profile.address)
            profile.save()

        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        return instance


class UpdatePassword(ModelSerializer):

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    retype_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = models.User
        fields = ('old_password', 'new_password', 'retype_password')


    def validate(self, attrs):
        if attrs['new_password'] != attrs['retype_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
    def validate_new_password(self, value):
        return validate_password(value)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance

# Customize claim to get username from token
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customising Login serialiser"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token
    
    def validate(self, attrs):
        try:
            tokens = super().validate(attrs)
            user = models.User.objects.get(username=self.user)
            user_data = UserModelSerializer(user)
            data = user_data.data
            data['tokens'] = tokens
        except Exception as e:
            print("-------------------------------------------------Hello")
            raise serializers.ValidationError(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        # Custom data you want to include
        
        
        return data

class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        tokens=""
        try:
            tokens = super().validate(attrs)
        except Exception as e:
            raise serializers.ValidationError(e)
        return tokens   

class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)

class VerifyPasswordResetSerializer(ModelSerializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    retype_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = models.User
        fields = ('new_password', 'retype_password')


    def validate(self, attrs):
        if attrs['new_password'] != attrs['retype_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
    def validate_new_password(self, value):
        return validate_password(value)

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance