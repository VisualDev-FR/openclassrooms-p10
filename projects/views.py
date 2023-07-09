from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from projects.serializers import ProjectSerializer, ContributorSerializer
from projects.models import Project, Contributor


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, project: Project):
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True
        else:
            return project.author.pk == request.user.pk


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):

        queryset = Project.objects.all()

        description = self.request.GET.get("description", None)

        if description is not None:
            queryset = queryset.filter(description=description)

        return queryset.order_by("id")

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        Contributor.objects.create(
            project=serializer.instance,
            user=serializer.instance.author,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ContributorViewSet(viewsets.ModelViewSet):

    queryset = Contributor.objects.all().order_by("project_id")
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]
