from rest_framework import viewsets, permissions, authentication, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from user.serializers import SoftdeskUserSerializer
from user.models import SoftdeskUser


class UserPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        else:
            return request.user.pk == obj.pk


class UserViewSet(viewsets.ModelViewSet):

    queryset = SoftdeskUser.objects.all()
    serializer_class = SoftdeskUserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        UserPermission
    ]

    def get_queryset(self):

        queryset = SoftdeskUser.objects.all()

        username = self.request.GET.get("username", None)

        if username is not None:
            queryset = queryset.filter(username=username)

        return queryset.order_by("id")

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RegisterView(CreateAPIView):

    serializer_class = SoftdeskUserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [authentication.SessionAuthentication]
