from django.utils.translation import gettext_lazy as _
from user.models import SoftdeskUser
from django.db import models


class Project(models.Model):

    class ProjectType(models.TextChoices):
        FRONTEND = "FRONT", _("front-end")
        BACKEND = "BACK", _("back-end")
        ANDROID = "ANDROID", _("android")
        IOS = "IOS", _("IOS")

    description = models.CharField(
        max_length=2000
    )

    type = models.CharField(
        max_length=10,
        choices=ProjectType.choices,
        default=ProjectType.FRONTEND,
    )

    author = models.ForeignKey(
        to=SoftdeskUser,
        on_delete=models.CASCADE,
    )


class Contributor(models.Model):
    """
    Relation between a project and a user
    """

    user = models.ForeignKey(
        to=SoftdeskUser,
        on_delete=models.CASCADE
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE
    )
