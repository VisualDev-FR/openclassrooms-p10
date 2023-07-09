from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from projects.models import Project, Contributor


class Issue(models.Model):

    class IssueTag(models.TextChoices):
        BUG = "BUG", _("bug")
        TODO = "TODO", _("todo")
        FEATURE = "FEATURE", _("feature")

    class IssueState(models.TextChoices):
        IN_WORK = "INWORK", _("in_work")
        RELEASED = "RELEASED", _("released")

    created_time = models.DateTimeField(auto_now=True)

    tag = models.CharField(
        max_length=10,
        choices=IssueTag.choices
    )

    state = models.CharField(
        max_length=10,
        choices=IssueState.choices,
        default=IssueState.IN_WORK
    )

    title = models.CharField(
        max_length=100
    )

    description = models.CharField(
        max_length=2000,
        default=""
    )

    priority = models.SmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        to=Contributor,
        on_delete=models.CASCADE,
        related_name='issue_author'
    )

    assigned_user = models.ForeignKey(
        to=Contributor,
        on_delete=models.CASCADE,
        null=True,
        related_name='issue_assigned_user'
    )
