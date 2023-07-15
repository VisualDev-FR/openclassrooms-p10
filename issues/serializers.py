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

    def validate_issue(self, value):
        if self.instance:
            raise serializers.ValidationError("the issue of a comment cant be modified")
        else:
            return value

    def validate_author(self, value):
        if self.instance:
            raise serializers.ValidationError("the author of a comment cant be modified")
        else:
            return value

    class Meta:
        model = Comment
        fields = "__all__"
