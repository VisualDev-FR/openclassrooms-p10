from rest_framework import viewsets, permissions
from issues.models import Issue, Comment
from issues.serializers import IssueSerializer, CommentSerializer
from projects.models import Contributor


class IssuesPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        project_id = request.data.get("project")
        author_id = request.data.get("author")

        user_is_contributor = Contributor.is_contributor(user.pk, project_id)
        create_for_himself = str(user.pk) == author_id

        if request.method in ["GET", "PATCH", "DELETE"]:
            # will be handled in IssuesPermission.has_object_permission() or in IssueViewSet.get_queryset()
            return True

        if request.method == "POST":
            return user_is_contributor and create_for_himself

        # any request out of CRUD will fail
        return False

    def has_object_permission(self, request, view, issue: Issue):

        is_author = issue.author.pk == request.user.pk
        user_is_contributor = Contributor.is_contributor(user_id=request.user.pk, project_id=issue.id)

        if request.method in permissions.SAFE_METHODS:
            return user_is_contributor
        else:
            return is_author


class CommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        issue_id = request.data.get("issue")
        issue = Issue.objects.filter(pk=issue_id)

        if not issue.exists():
            # will be handled by serializer validators
            return True

        project_id = issue[0].project.pk

        user = request.user
        user_is_contributor = Contributor.is_contributor(user.pk, project_id)

        author_id = request.data.get("author")
        create_for_himself = str(user.pk) == author_id

        if request.method in ["GET", "PATCH", "DELETE"]:
            # will be handled in CommentPermission.has_object_permission() or in CommentViewset.get_queryset()
            return True

        if request.method == "POST":
            return user_is_contributor and create_for_himself

        # any request out of CRUD will fail
        return False

    def has_object_permission(self, request, view, comment: Comment):

        project_id = comment.issue.project.pk

        user_is_contributor = Contributor.is_contributor(user_id=request.user.pk, project_id=project_id)
        user_is_author = comment.author.pk == request.user.pk

        if request.method in permissions.SAFE_METHODS:
            return user_is_contributor
        else:
            return user_is_author


class IssueViewSet(viewsets.ModelViewSet):

    queryset = Issue.objects.all().order_by("created_time")
    serializer_class = IssueSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IssuesPermission
    ]

    def get_queryset(self):

        user_accessible_projects = Contributor.get_user_projects(self.request.user.pk)
        user_accessible_issues = Issue.objects.filter(project_id__in=user_accessible_projects)

        self.queryset = user_accessible_issues

        title = self.request.GET.get("title", None)

        if title is not None:
            self.queryset = self.queryset.filter(title=title)

        return self.queryset.order_by("created_time")


class CommentViewset(viewsets.ModelViewSet):

    queryset = Comment.objects.all().order_by("created_time")
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CommentPermission
    ]

    def get_queryset(self):

        user_accessible_projects = Contributor.get_user_projects(self.request.user.pk)
        user_accessible_issues = Issue.objects.filter(project_id__in=user_accessible_projects)
        user_accessible_comments = Comment.objects.filter(issue_id__in=user_accessible_issues)

        self.queryset = user_accessible_comments

        return self.queryset.order_by("created_time")
