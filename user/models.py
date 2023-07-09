from django.db import models
from django.contrib.auth.models import User


class SoftdeskUser(User):
    """
    Custom user, with attributes specific to the softdesk application
    """

    # define a multi-table-inheritance across this field.
    # see : https://docs.djangoproject.com/en/4.2/topics/db/models/#multi-table-inheritance
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True
    )

    age = models.IntegerField()
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
