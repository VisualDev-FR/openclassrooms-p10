from user.models import SoftdeskUser
from rest_framework import serializers
from django.contrib.auth.hashers import make_password


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
            'password',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
