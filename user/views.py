from rest_framework import viewsets
from rest_framework import permissions
from user.serializers import SoftdeskUserSerializer
from user.models import SoftdeskUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = SoftdeskUser.objects.all()
    serializer_class = SoftdeskUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        queryset = SoftdeskUser.objects.all()

        username = self.request.GET.get("username", None)

        if username is not None:
            queryset = queryset.filter(username=username)

        return queryset.order_by("id")
