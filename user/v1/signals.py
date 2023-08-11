from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from user import models
from user.v1.views import LogoutView
from django.contrib.auth.signals import user_logged_in

from utils.sendEmail import send_verification_email

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


@receiver(signal=post_save, sender=models.User)
def on_change(sender, instance, created, **kwargs):
    if not instance.is_verified and not created:
        send_verification_email(user=instance, subject="Verify Email id", content="Email update successful. Please verify the updated email id by clinking the below link")