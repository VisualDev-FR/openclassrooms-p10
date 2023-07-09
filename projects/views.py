from rest_framework import viewsets, permissions
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
        """
        Override queryset getter, in order to add custom filters
        """
        queryset = Project.objects.all()

        description = self.request.GET.get("description", None)

        if description is not None:
            queryset = queryset.filter(description=description)

        return queryset.order_by("id")


class ContributorViewSet(viewsets.ModelViewSet):

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]
