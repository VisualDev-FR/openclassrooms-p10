from rest_framework.test import APITestCase
from issues.models import Issue
from user.models import SoftdeskUser
from projects.models import Project, Contributor


class TestIssue(APITestCase):

    def setUp(self) -> None:

        self.author = SoftdeskUser.objects.create_user(
            username="admin",
            password="password",
            age=27,
        )

        self.client.force_login(self.author)

        self.project = Project.objects.create(
            description="project",
            type="FRONT",
            author=self.author
        )

        self.assertEqual(Contributor.objects.all().count(), 1)

        self.issue = Issue.objects.create(
            tag="TODO",
            title="TODO Issue",
            project=self.project,
            author=Contributor.objects.get(pk=1)
        )

    def test_get_issue(self):

        response = self.client.get("/issues/")

        self.assertEqual(response.status_code, 200)
