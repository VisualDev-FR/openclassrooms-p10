from rest_framework import serializers
from projects.models import Project, Contributor
from user.serializers import SoftdeskUserSerializer
from user.models import SoftdeskUser


class ProjectSerializer(serializers.ModelSerializer):

    def validate_author(self, author_id):
        """
        Allow to prevent the author update
        """
        if self.instance:
            raise serializers.ValidationError("update the project author is not allowed")

        return author_id

    def to_representation(self, instance):
        data = super().to_representation(instance)

        author = SoftdeskUserSerializer(
            SoftdeskUser.objects.get(pk=data['author'])
        )

        data["author"] = author.data

        return data

    class Meta:
        model = Project
        fields = "__all__"


class ContributorSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):

        data = super().to_representation(instance)

        project = ProjectSerializer(
            Project.objects.get(pk=data['project'])
        )

        user = SoftdeskUserSerializer(
            SoftdeskUser.objects.get(pk=data['user'])
        )

        data['project'] = project.data
        data['user'] = user.data

        return data

    class Meta:
        model = Contributor
        fields = "__all__"
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Contributor.objects.all(),
                fields=["user", "project"]
            )
        ]
