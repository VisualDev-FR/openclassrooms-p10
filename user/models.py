from django.db import models
from django.contrib.auth.models import User


class SoftdeskUser(User):
    """ Custom user, with attributes specific to the softdesk application """
    age = models.IntegerField()
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
