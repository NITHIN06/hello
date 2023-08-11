from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.db import models

from utils import models as u_models

# Create your models here.
class Advertisement(u_models.TimeStampedModel):

    class STATUS(models.IntegerChoices):
        active = 1, _("active")
        inactive = 2, _("inactive")
        sold = 3, _("sold")
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    status = models.IntegerField(
        choices=STATUS.choices,
        default=STATUS.active
    )
    is_archive = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(default=None, null=True, blank=True)
    is_agent = models.BooleanField(default=False)

    # category = models.ForeignKey()

    price = models.DecimalField(max_digits=50, decimal_places=5)
    negotiable = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    # plan = models.ForeignKey()

    latitude = models.FloatField() # min_value = -90, max_value = 90
    longitude = models.FloatField() # min_value = -180, max_value = 180

    purchased_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer'
    )
    seller_name = models.CharField(max_length=30)
    contact_email = models.EmailField(max_length=50)
    contact_phone = models.CharField(max_length=13)