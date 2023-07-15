from rest_framework import viewsets, permissions
from projects.serializers import ProjectSerializer, ContributorSerializer
from projects.models import Project, Contributor
from rest_framework import status
from rest_framework.response import Response


class ProjectPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        author_id = request.data.get("author")
        create_for_himself = str(request.user.pk) == author_id

        if request.method in ["GET", "PATCH", "DELETE"]:
            # will be handled in ProjectPermission.has_object_permission() or in IssueViewSet.get_queryset()
            return True

        if request.method == "POST":
            return create_for_himself

        # any request out of CRUD will fail
        return False

    def has_object_permission(self, request, view, project: Project):

        is_author = project.author.pk == request.user.pk
        is_contributor = Contributor.objects.filter(user_id=request.user.pk, project_id=project.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_contributor
        else:
            return is_author


class ContributorPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in ["POST"]:

            project_id = request.data.get("project")
            project = Project.objects.filter(pk=project_id)

            if project.exists():
                # the user who tries to create a contributor must be the project author
                user_is_author = project[0].author.pk == request.user.pk
                return user_is_author

            else:
                # the post request will fail if no project is specified
                pass

        return True

    def has_object_permission(self, request, view, obj: Contributor):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return obj.project.author.pk == request.user.pk

        return False


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        ProjectPermission
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


class ContributorViewSet(viewsets.ModelViewSet):

    queryset = Contributor.objects.all().order_by("user_id")
    serializer_class = ContributorSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        ContributorPermission
    ]

    def get_queryset(self):

        user_accessible_projects = Contributor.get_user_projects(self.request.user.pk)
        user_accessible_contributors = Contributor.objects.filter(project_id__in=user_accessible_projects)

        self.queryset = user_accessible_contributors

        user = self.request.GET.get("user")
        project = self.request.GET.get("project")

        if user:
            self.queryset = self.queryset.filter(user_id=user)

        if project:
            self.queryset = self.queryset.filter(project_id=project)

        return self.queryset.order_by("created_time")

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
