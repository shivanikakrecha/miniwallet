import uuid
from django.db import models
from base.models import BaseModel
from django.conf import settings
from django.core.validators import RegexValidator


# Create your models here.
class Customer(BaseModel):
    """ `Customer` model to store the information of customer.
    """
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female")
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name='customer', verbose_name="User"
    )
    customer_id = models.UUIDField(
        default=uuid.uuid4, editable=False
    )
    account_name = models.CharField(
        verbose_name='Account Name', max_length=255, help_text='Customer Account Name'
    )
    account_number = models.CharField(
        verbose_name='Customer Account Number', max_length=255, unique=True, default='000000000000',
        help_text='Number of the account'
    )
    customer_address = models.TextField(
        verbose_name="Customer Address", null=True, blank=True, help_text="Customer Address"
    )
    mobile_number_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+9999999999'. Up to 15 digits allowed."
    )
    mobile_number = models.CharField(
        validators=[mobile_number_regex], max_length=17, blank=True, null=True,
        verbose_name="Customer Mobile Number"
    )
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=1, verbose_name="Customer Gender", default="M"
    )

    class Meta:
        unique_together = [['customer_id', 'account_number']]

    def __str__(self):
        return self.user.email
