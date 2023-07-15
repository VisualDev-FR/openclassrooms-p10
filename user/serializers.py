from user.models import SoftdeskUser
from rest_framework import serializers


class SoftdeskUserSerializer(serializers.ModelSerializer):

    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError("User must be at least 15 years old.")
        else:
            return value

    class Meta:
        model = SoftdeskUser
        fields = [
            'id',
            'username',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]
