from rest_framework import viewsets, permissions, mixins
from projects.serializers import ProjectSerializer, ContributorSerializer
from projects.models import Project, Contributor


class IsAuthorOrContributor(permissions.BasePermission):

    def has_object_permission(self, request, view, project: Project):

        is_author = project.author.pk == request.user.pk
        is_contributor = Contributor.objects.filter(user_id=request.user.pk, project_id=project.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_contributor
        else:
            return is_author


class ContributorDestroyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Contributor):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.project.author.pk == request.user.pk


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAuthorOrContributor
    ]

    def get_queryset(self):
        """
        Override queryset getter, in order to add custom filters
        """

        user = self.request.user
        contributor_projects = Contributor.objects.filter(user=user).values_list("project_id", flat=True)
        self.queryset = Project.objects.filter(id__in=contributor_projects)

        description = self.request.GET.get("description", None)

        if description is not None:
            self.queryset = self.queryset.filter(description=description)

        return self.queryset.order_by("created_time")


class ContributorViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    queryset = Contributor.objects.all().order_by("user_id")
    serializer_class = ContributorSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        ContributorDestroyPermission
    ]

    # BUG: check before create : django.db.utils.IntegrityError: UNIQUE constraint failed: projects_contributor.user_id, projects_contributor.project_id
