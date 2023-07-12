from rest_framework.test import APITestCase
from issues.models import Issue
from user.models import SoftdeskUser
from projects.models import Project, Contributor


class TestIssue(APITestCase):

    def setUp(self) -> None:

        self.author = SoftdeskUser.objects.create_user(
            username="author",
            password="password",
            age=27,
        )

        self.non_author = SoftdeskUser.objects.create_user(
            username="non_author",
            password="password",
            age=27,
        )

        self.project = Project.objects.create(
            description="project",
            type="FRONT",
            author=self.author
        )

        self.assertEqual(Contributor.objects.all().count(), 1)

        self.issue = Issue.objects.create(
            tag="TODO",
            title="TODO Issue",
            description="Issue description",
            project=self.project,
            author=Contributor.objects.get(pk=1)
        )

    # CREATE
    def test_create_minimal_issue(self):

        self.client.force_login(self.author)
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
        })

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Issue.objects.count(), 2)

    def test_create_issue_with_missing_datas(self):

        self.client.force_login(self.author)

        # create issue without author
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())

        # create issue without project
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "author": self.author.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())

        # create issue without title
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "project": self.project.pk,
            "author": self.author.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())

        # create issue without tag
        response = self.client.post("/issues/", data={
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())

        self.assertEqual(Issue.objects.count(), 1)

    def test_create_issue_from_contributor(self):

        self.client.force_login(self.non_author)

        Contributor.objects.create(
            project=self.project,
            user=self.non_author
        )

        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.non_author.pk,
        })

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Issue.objects.count(), 2)

    def test_create_issue_from_unauthorized(self):

        # create from an non authenticated user
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
        })

        self.assertEqual(response.status_code, 403, response.json())
        self.assertEqual(Issue.objects.count(), 1)

        # create from a user who is not a project contributor
        self.client.force_login(self.non_author)

        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
        })

        self.assertEqual(response.status_code, 403, response.json())
        self.assertEqual(Issue.objects.count(), 1)

    def test_create_issue_for_other_user(self):

        self.client.force_login(self.author)

        Contributor.objects.create(
            user=self.non_author,
            project=self.project
        )

        # create from an non authenticated user
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.non_author.pk,
        })

        self.assertEqual(response.status_code, 403, response.json())
        self.assertEqual(Issue.objects.count(), 1)

    # RETREIVE
    def test_get_issue_from_author(self):

        self.client.force_login(self.author)

        response = self.client.get("/issues/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

        response = self.client.get("/issues/1/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "TODO Issue", response.json())

    def test_get_issue_from_contributor(self):

        self.client.force_login(self.non_author)

        Contributor.objects.create(
            project=self.project,
            user=self.non_author
        )

        response = self.client.get("/issues/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

        response = self.client.get("/issues/1/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "TODO Issue", response.json())

    def test_get_issue_from_non_authorized(self):

        # retreive from non authenticated user
        response = self.client.get("/issues/")
        self.assertEqual(response.status_code, 403)

        response = self.client.get("/issues/1/")
        self.assertEqual(response.status_code, 403)

        # retreive from user who is not a project contributor
        self.client.force_login(self.non_author)

        response = self.client.get("/issues/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get("/issues/1/")
        self.assertEqual(response.status_code, 404)

    # UPDATE
    def test_update_issue(self):

        self.client.force_login(self.author)

        response = self.client.patch("/issues/1/", data={
            "tag": "BUG",
            "title": "BUG Issue"
        })

        self.assertEqual(response.status_code, 200)

        updated_issue = Issue.objects.get(pk=1)

        self.assertEqual(updated_issue.tag, "BUG")
        self.assertEqual(updated_issue.title, "BUG Issue")
        self.assertEqual(updated_issue.description, "Issue description")

    def test_update_issue_from_unauthorized(self):

        # update from non authenticated user
        response = self.client.patch("/issues/1/", data={
            "tag": "BUG",
            "title": "BUG Issue"
        })

        self.assertEqual(response.status_code, 403)

        # update from non contributor / non author user
        self.client.force_login(self.non_author)

        response = self.client.patch("/issues/1/", data={
            "tag": "BUG",
            "title": "BUG Issue"
        })

        self.assertEqual(response.status_code, 404)

        updated_issue = Issue.objects.get(pk=1)

        self.assertEqual(updated_issue.tag, "TODO")
        self.assertEqual(updated_issue.title, "TODO Issue")

    def test_update_issue_from_contributor(self):

        # register user as a project contributor who is not the issue author
        self.client.force_login(self.non_author)

        Contributor.objects.create(
            user=self.non_author,
            project=self.project
        )

        response = self.client.patch("/issues/1/", data={
            "tag": "BUG",
            "title": "BUG Issue"
        })

        self.assertEqual(response.status_code, 403)

        updated_issue = Issue.objects.get(pk=1)

        self.assertEqual(updated_issue.tag, "TODO")
        self.assertEqual(updated_issue.title, "TODO Issue")

    # DELETE
    def test_delete_issue(self):

        self.client.force_login(self.author)

        response = self.client.delete("/issues/1/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Issue.objects.exists())

    def test_delete_issue_from_unauthorized(self):

        # delete from non authenticated user
        response = self.client.delete("/issues/1/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Issue.objects.count(), 1)

        # delete from non author user
        self.client.force_login(self.non_author)

        response = self.client.delete("/issues/1/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Issue.objects.count(), 1)

    def test_delete_issue_from_contributor(self):

        # register user as a project contributor who is not the issue author
        self.client.force_login(self.non_author)

        Contributor.objects.create(
            user=self.non_author,
            project=self.project
        )

        # delete from non authenticated user
        response = self.client.delete("/issues/1/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Issue.objects.count(), 1)
