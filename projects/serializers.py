from rest_framework import serializers
from projects.models import Project, Contributor
from user.serializers import SoftdeskUserSerializer
from user.models import SoftdeskUser


class ProjectSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        author = SoftdeskUserSerializer(
            SoftdeskUser.objects.get(pk=data['author'])
        )

        data["author"] = author.data

        return data

    class Meta:
        model = Project
        fields = [
            'description',
            'type',
            'author',
        ]


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
        fields = [
            'id',
            'url',
            'user',
            'project',
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Contributor.objects.all(),
                fields=["user", "project"]
            )
        ]
