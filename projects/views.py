from rest_framework import viewsets
from rest_framework import permissions
from projects.serializers import ProjectSerializer, ContributorSerializer
from projects.models import Project, Contributor


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, project: Project):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return project.author.pk == request.user.pk


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):

        queryset = Project.objects.all()

        description = self.request.GET.get("description", None)

        if description is not None:
            queryset = queryset.filter(description=description)

        return queryset.order_by("id")


class ContributorViewSet(viewsets.ModelViewSet):

    queryset = Contributor.objects.all().order_by("project_id")
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]
