from rest_framework.test import APITestCase
from issues.models import Issue, Comment
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
            author=self.author
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
        self.assertEqual(response.status_code, 403, response.json())

        # create issue without project
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "author": self.author.pk,
        })
        self.assertEqual(response.status_code, 403, response.json())

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

        # create an issue with another user as author
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.non_author.pk,
        })

        self.assertEqual(response.status_code, 403, response.json())
        self.assertEqual(Issue.objects.count(), 1)

    def test_create_issue_with_assigned_contributor(self):

        self.client.force_login(self.author)

        Contributor.objects.create(
            project=self.project,
            user=self.non_author
        )

        # assignate another user
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
            "assigned_user": self.non_author.pk
        })

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Issue.objects.count(), 2)

        # assignate himself
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
            "assigned_user": self.author.pk
        })

        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Issue.objects.count(), 3)

    def test_create_issue_with_assigned_non_contributor(self):

        self.client.force_login(self.author)

        # assignate an user who is not registered as a project contributor
        response = self.client.post("/issues/", data={
            "tag": "BUG",
            "title": "fatal error",
            "project": self.project.pk,
            "author": self.author.pk,
            "assigned_user": self.non_author.pk
        })

        self.assertEqual(response.status_code, 400, response.json())
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

        self.assertEqual(response.status_code, 200, response.json())

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

        self.assertEqual(response.status_code, 404, response.json())

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

    def test_update_issue_with_assigned_contributor(self):

        self.client.force_login(self.author)

        Contributor.objects.create(
            user=self.non_author,
            project=self.project
        )

        response = self.client.patch("/issues/1/", data={
            "assigned_user": self.non_author.pk
        })

        self.assertEqual(response.status_code, 200, response.json())

        updated_issue = Issue.objects.get(pk=1)

        self.assertEqual(updated_issue.assigned_user.username, "non_author")

    def test_update_issue_with_assigned_non_contributor(self):

        self.client.force_login(self.author)

        response = self.client.patch("/issues/1/", data={
            "assigned_user": self.non_author.pk
        })

        self.assertEqual(response.status_code, 400, response.json())

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


class TestComment(APITestCase):

    def setUp(self) -> None:

        self.project_author = SoftdeskUser.objects.create_user(
            username="author",
            password="password",
            age=27,
        )

        self.project_contributor = SoftdeskUser.objects.create_user(
            username="non_author",
            password="password",
            age=27,
        )

        self.random_user = SoftdeskUser.objects.create_user(
            username="random_user",
            password="password",
            age=27,
        )

        self.project = Project.objects.create(
            description="project",
            type="FRONT",
            author=self.project_author
        )

        Contributor.objects.create(
            user=self.project_contributor,
            project=self.project
        )

        self.assertEqual(Contributor.objects.all().count(), 2)

        self.issue = Issue.objects.create(
            tag="TODO",
            title="TODO Issue",
            description="Issue description",
            project=self.project,
            author=self.project_author
        )

        self.comment = Comment.objects.create(
            issue=self.issue,
            author=self.project_author,
            description="useless comment, for testing purpose..."
        )

    # CREATE

    def test_create_minimal_comment(self):

        self.client.force_login(self.project_author)

        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.project_author.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 201, response.json())

    def test_create_comment_with_missing_datas(self):

        self.client.force_login(self.project_author)

        # create comment without issue
        response = self.client.post('/comments/', data={
            "author": self.project_author.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 400, response.json())

        # create comment without author
        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 403, response.json())

        # create comment without description
        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.project_author.pk,
        })

        self.assertEqual(response.status_code, 400, response.json())

    def test_create_comment_from_contributor(self):

        self.client.force_login(self.project_contributor)

        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.project_contributor.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 201, response.json())

    def test_create_comment_from_unauthorized(self):

        # create comment from non authenticated user
        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.project_contributor.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 403, response.json())

        # create comment from non contributor user
        self.client.force_login(self.random_user)

        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.random_user.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 403, response.json())

    def test_create_comment_for_other_user(self):

        self.client.force_login(self.project_author)

        response = self.client.post('/comments/', data={
            "issue": self.issue.pk,
            "author": self.project_contributor.pk,
            "description": "null description"
        })

        self.assertEqual(response.status_code, 403, response.json())

    # RETREIVE

    def test_get_comment_from_project_author(self):

        self.client.force_login(self.project_author)

        response = self.client.get("/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

        response = self.client.get("/comments/1/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['description'], "useless comment, for testing purpose...", response.json())

    def test_get_comment_from_project_contributor(self):

        self.client.force_login(self.project_contributor)

        response = self.client.get("/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

        response = self.client.get("/comments/1/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['description'], "useless comment, for testing purpose...", response.json())

    def test_get_comment_from_unauthorized_user(self):

        # get comments from non authenticated user
        response = self.client.get("/comments/")
        self.assertEqual(response.status_code, 403)

        response = self.client.get("/comments/1/")
        self.assertEqual(response.status_code, 403)

        # get comments from user who is not a project contributor
        self.client.force_login(self.random_user)
        response = self.client.get("/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get("/comments/1/")

        self.assertEqual(response.status_code, 404)

    # UPDATE

    def test_update_comment(self):
        pass

    # DELETE
