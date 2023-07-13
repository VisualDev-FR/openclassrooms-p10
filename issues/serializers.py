from issues.models import Issue
from projects.models import Contributor
from rest_framework import serializers


class IssueSerializer(serializers.ModelSerializer):

    def validate(self, data: dict):
        """
        See https://www.django-rest-framework.org/api-guide/serializers/#object-level-validation
        """

        project_id = data.get("project") or self.instance.project.pk
        author_id = data.get("author") or self.instance.author.pk
        assigned_user_id = data.get("assigned_user")

        author_is_contributor = Contributor.is_contributor(author_id, project_id)
        assigned_user_is_contributor = Contributor.is_contributor(assigned_user_id, project_id)

        if not author_is_contributor:
            raise serializers.ValidationError("author must be a project contributor")

        if assigned_user_id and not assigned_user_is_contributor:
            raise serializers.ValidationError("assigned user must be a project contributor")

        return data

    class Meta:
        model = Issue
        fields = "__all__"
