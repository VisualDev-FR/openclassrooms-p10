from django.utils.translation import gettext_lazy as _
from django.db import models
from projects.models import Project
from user.models import SoftdeskUser


class Issue(models.Model):

    class IssueTag(models.TextChoices):
        BUG = "BUG", _("bug")
        TASK = "TASK", _("task")
        FEATURE = "FEATURE", _("feature")

    class IssueState(models.TextChoices):
        TODO = "TODO", _("todo")
        IN_WORK = "INWORK", _("in_work")
        RELEASED = "RELEASED", _("released")

    class IssuePriority(models.TextChoices):
        LOW = "LOW", _("low")
        MEDIUM = "MEDIUM", _("medium")
        HIGH = "HIGH", _("high")

    created_time = models.DateTimeField(auto_now=True)

    tag = models.CharField(
        max_length=10,
        choices=IssueTag.choices
    )

    state = models.CharField(
        max_length=10,
        choices=IssueState.choices,
        default=IssueState.TODO
    )

    title = models.CharField(
        max_length=100
    )

    description = models.CharField(
        max_length=2000,
        default=""
    )

    priority = models.CharField(
        max_length=10,
        choices=IssuePriority.choices,
        default=IssuePriority.LOW
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        to=SoftdeskUser,
        on_delete=models.CASCADE,
        related_name='issue_author'
    )

    assigned_user = models.ForeignKey(
        to=SoftdeskUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='issue_assigned_user'
    )


class Comment(models.Model):

    issue = models.ForeignKey(
        to=Issue,
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        to=SoftdeskUser,
        on_delete=models.CASCADE
    )

    description = models.CharField(
        max_length=2000
    )

    created_time = models.DateTimeField(
        auto_now=True
    )
