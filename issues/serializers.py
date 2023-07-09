from issues.models import Issue
from rest_framework import serializers


class IssueSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return super().to_representation(instance)

    class Meta:
        model = Issue
        fields = "__all__"
