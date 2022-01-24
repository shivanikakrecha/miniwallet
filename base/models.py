from django.db import models


# Create your models here.
class BaseModel(models.Model):
    """ Default Django model extended to provide common fields.
    For auditing, logging etc.
    """

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
