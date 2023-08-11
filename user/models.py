from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from utils import models as u_models
from django.contrib.auth import get_user_model


class AllObjects(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
class UserManager(BaseUserManager):
    def create_user(self, name, email, username, password=None, **extra_fields):
        """Mehtod to handle custom user registration"""
        if not email or not username:
            raise ValueError('Email and Username fields should not be empty')
        
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)
    
    def create_superuser(self, name, email, username, password):
        """Method to create super user (with custom user model)"""
        user = self.create_user(name, email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin, u_models.TimeStampedModel):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    all_objects = AllObjects()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']


    def get_full_name(self):
        """Retrieve full name of user"""
        return self.name

    def get_short_name(self):
        """Retrieve shot name of user"""
        return self.name

    def __str__(self):
        return self.username

class AccessTokenBlacklist(models.Model):
    '''Model to store blacklisted tokens'''
    token = models.CharField(max_length=500)
    user = models.ForeignKey(get_user_model(), related_name="accesstoken_user", on_delete=models.CASCADE,null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")


def user_directory_path(instance, filename):
    return 'images/user_{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    # username = models.CharField(max_length=30,null=True)
    phone = models.CharField(max_length=13,null=True)
    address = models.CharField(max_length=50,null=True)
    img_location = models.ImageField(upload_to=user_directory_path, max_length=100, null=True)
    # img_location = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)