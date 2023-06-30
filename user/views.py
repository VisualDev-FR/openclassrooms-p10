from rest_framework import viewsets
from rest_framework import permissions
from user.serializers import SoftdeskUserSerializer
from user.models import SoftdeskUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = SoftdeskUser.objects.all().order_by('-date_joined')
    serializer_class = SoftdeskUserSerializer
    permission_classes = [permissions.IsAuthenticated]
