from user.models import SoftdeskUser
from rest_framework import serializers


class SoftdeskUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SoftdeskUser
        fields = [
            'url',
            'username',
            'password',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]
