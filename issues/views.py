from rest_framework import viewsets, permissions
from issues.models import Issue
from issues.serializers import IssueSerializer
from projects.models import Contributor
from rest_framework.response import Response
from rest_framework import status


class IsAuthorOrContributor(permissions.BasePermission):

    def has_object_permission(self, request, view, issue: Issue):

        is_author = issue.author.pk == request.user.pk
        user_is_contributor = Contributor.is_contributor(user_id=request.user.pk, project_id=issue.id)

        if request.method in permissions.SAFE_METHODS:
            return user_is_contributor
        else:
            return is_author


class IssueViewSet(viewsets.ModelViewSet):

    queryset = Issue.objects.all().order_by("created_time")
    serializer_class = IssueSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAuthorOrContributor
    ]

    def get_queryset(self):

        user = self.request.user
        contributor_projects = Contributor.objects.filter(user=user).values_list("project_id", flat=True)
        self.queryset = Issue.objects.filter(project_id__in=contributor_projects)

        title = self.request.GET.get("title", None)

        if title is not None:
            self.queryset = self.queryset.filter(title=title)

        return self.queryset.order_by("created_time")

    def create(self, request, *args, **kwargs):

        self.get_serializer(data=request.data).is_valid(raise_exception=True)

        user = request.user
        project_id = request.data.get("project")
        author_id = request.data.get("author")

        user_is_contributor = Contributor.is_contributor(user.pk, project_id)
        create_for_himself = str(user.pk) == author_id

        if not user_is_contributor:
            return Response({"author": "you must be registered as a project contributor to create an issue"}, status=status.HTTP_403_FORBIDDEN)

        if not create_for_himself:
            return Response({"author": "you cannot create an issue with someone else as an author"}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)
