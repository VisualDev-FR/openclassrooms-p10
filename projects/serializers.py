from rest_framework import serializers
from projects.models import Project, Contributor
from user.serializers import SoftdeskUserSerializer


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'url',
            'description',
            'type',
            'author',
        ]


class ContributorSerializer(serializers.ModelSerializer):

    user = SoftdeskUserSerializer()
    project = ProjectSerializer()

    class Meta:
        model = Contributor
        fields = [
            'url',
            'user',
            'project',
        ]
