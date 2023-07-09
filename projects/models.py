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

    created_time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Override default save method, in order to add auto creation of contributor
        """

        # apply the regular parent save method
        project = super().save(*args, **kwargs)

        # create a contributor between author and created project
        Contributor.objects.create(
            project=self,
            user=self.author,
        )

        # parent save method return
        return project


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
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('user', 'project')