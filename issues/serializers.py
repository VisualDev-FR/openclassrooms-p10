from issues.models import Issue, Comment
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
            raise serializers.ValidationError("the issue author must be a project contributor")

        if assigned_user_id and not assigned_user_is_contributor:
            raise serializers.ValidationError("the assigned user must be a project contributor")

        return data

    def validate_author(self, author_id):

        if self.instance:
            raise serializers.ValidationError("update the author of an issue is not allowed")
        else:
            return author_id

    def validate_project(self, project_id):
        if self.instance:
            raise serializers.ValidationError("update the project of an issue is not allowed")
        else:
            return project_id

    class Meta:
        model = Issue
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):

    # TODO: CommentSerializer.to_representation()
    def to_representation(self, instance):
        return super().to_representation(instance)

    def validate(self, data: dict):

        issue_changed = False
        author_changed = False

        if self.instance and data.get("issue"):
            issue_changed = self.instance.issue.pk != data.get("issue")

        if self.instance and data.get("author"):
            author_changed = self.instance.author.pk != data.get("author")

        if issue_changed:
            raise serializers.ValidationError("the issue of a comment cant be modified")

        if author_changed:
            raise serializers.ValidationError("the author of a comment cant be modified")

        return data

    class Meta:
        model = Comment
        fields = "__all__"
