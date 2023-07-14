from rest_framework.test import APITestCase
from user.models import SoftdeskUser
from projects.models import Project, Contributor


class TestProject(APITestCase):

    def setUp(self) -> None:

        self.project_author = SoftdeskUser.objects.create_user(
            username="project_author",
            password="password",
            age=27,
        )

        self.project_contributor = SoftdeskUser.objects.create_user(
            username="project_contributor",
            password="password",
            age=27,
        )

        self.random_user = SoftdeskUser.objects.create_user(
            username="random_user",
            password="password",
            age=27,
        )

        self.project = Project.objects.create(
            description="existing_project",
            type="FRONT",
            author=self.project_author
        )

        Contributor.objects.create(
            project=self.project,
            user=self.project_contributor
        )

    # CREATE
    def test_create_project(self):

        self.client.force_login(self.random_user)

        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "FRONT",
            "author": self.random_user.pk
        })
        self.assertEqual(response.status_code, 201, response.json())
        self.assertTrue(Contributor.objects.filter(user=self.random_user, project_id=2).exists())

    def test_create_project_without_author(self):

        self.client.force_login(self.random_user)

        # create new project without specifiying author
        response = self.client.post("/projects/", data={
            "description": "Dummy description",
            "type": "FRONT",
        })

        # assert that the request was rejected
        self.assertEqual(response.status_code, 403, response.json())

    def test_create_project_with_invalid_type(self):

        self.client.force_login(self.random_user)

        # create new project with invalid type
        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "Invalid type",
            "author": self.random_user.pk
        })

        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(response.json(), {'type': ['"Invalid type" is not a valid choice.']}, response.json())

    def test_create_project_for_another_user(self):

        self.client.force_login(self.random_user)

        # create new project
        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "FRONT",
            "author": self.project_author.pk
        })
        self.assertEqual(response.status_code, 403, response.json())

    def test_create_project_from_non_authenticated_user(self):

        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "FRONT",
            "author": self.random_user.pk
        })
        self.assertEqual(response.status_code, 403, response.json())

    # RETREIVE
    def test_get_project_from_author(self):

        self.client.force_login(self.project_author)

        # get all projects
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        # get one project
        response = self.client.get("/projects/1/")
        self.assertEqual(response.status_code, 200)

    def test_get_project_from_contributor(self):

        self.client.force_login(self.project_contributor)

        # get all projects
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        # get one project
        response = self.client.get("/projects/1/")
        self.assertEqual(response.status_code, 200)

    def test_get_project_from_unauthorized(self):

        # get projects from non authenticated user
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 403)

        response = self.client.get("/projects/1/")
        self.assertEqual(response.status_code, 403)

        # get projects from a user who is not a project contributor
        self.client.force_login(self.random_user)
        response = self.client.get("/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get("/projects/1/")
        self.assertEqual(response.status_code, 404)

    # UPDATE
    def test_update_project_from_author(self):

        self.client.force_login(self.project_author)

        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        updated_project = Project.objects.get(pk=1)

        # assert update was sucessfully applied
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_project.type, "BACK")

    def test_update_project_from_non_author(self):

        # update project from non authenticated user
        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        self.assertEqual(response.status_code, 403, response.json())

        # update project from contributor user
        self.client.force_login(self.project_contributor)
        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        self.assertEqual(response.status_code, 403, response.json())

        # update project from non contributor user
        self.client.force_login(self.random_user)
        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        self.assertEqual(response.status_code, 404, response.json())

    def test_update_forbidden_datas(self):

        self.client.force_login(self.project_author)

        response = self.client.patch("/projects/1/", data={
            "author": self.random_user.pk,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'author': ['update the project author is not allowed']}, response.json())

    # DELETE
    def test_delete_project_from_author(self):

        self.client.force_login(self.project_author)

        # delete the desired project
        response = self.client.delete("/projects/1/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Project.objects.filter(pk=1).exists())

    def test_delete_project_from_non_author(self):

        # delete the from non authenticated user
        response = self.client.delete("/projects/1/")
        self.assertEqual(response.status_code, 403)

        # delete the from contributor user
        self.client.force_login(self.project_contributor)
        response = self.client.delete("/projects/1/")
        self.assertEqual(response.status_code, 403)

        # delete the from non contributor user
        self.client.force_login(self.random_user)
        response = self.client.delete("/projects/1/")
        self.assertEqual(response.status_code, 404)

        self.assertTrue(Project.objects.filter(pk=1).exists())


class TestContributor(APITestCase):

    def setUp(self) -> None:

        self.project_author = SoftdeskUser.objects.create_user(
            username="project_author",
            password="password",
            age=27,
        )

        self.project_contributor = SoftdeskUser.objects.create_user(
            username="project_contributor",
            password="password",
            age=27,
        )

        self.random_user = SoftdeskUser.objects.create_user(
            username="random_user",
            password="password",
            age=27,
        )

        self.project = Project.objects.create(
            description="existing_project",
            type="FRONT",
            author=self.project_author
        )

        Contributor.objects.create(
            project=self.project,
            user=self.project_contributor
        )

    # CREATE
    def test_create_contributor_from_project_author(self):

        self.client.force_login(self.project_author)

        response = self.client.post("/contributors/", data={
            "user": self.random_user.pk,
            "project": self.project.pk,
        })

        self.assertEqual(response.status_code, 201, response.json())

    def test_create_existing_contributor(self):

        self.client.force_login(self.project_author)

        response = self.client.post("/contributors/", data={
            "user": self.project_contributor.pk,
            "project": self.project.pk,
        })

        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(response.json(), {'non_field_errors': ['The fields user, project must make a unique set.']})

    def test_create_contributor_from_unauthorized(self):

        # create user from non authenticated user
        response = self.client.post("/contributors/", data={
            "user": self.random_user.pk,
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 403, response.json())

        # create user from project contributor
        self.client.force_login(self.project_contributor)
        response = self.client.post("/contributors/", data={
            "user": self.random_user.pk,
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 403, response.json())

        # create user from non contributor user
        self.client.force_login(self.random_user)
        response = self.client.post("/contributors/", data={
            "user": self.random_user.pk,
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 403, response.json())

    def test_create_contributor_with_missing_datas(self):

        self.client.force_login(self.project_author)

        # create contributor without project
        response = self.client.post("/contributors/", data={
            "user": self.random_user.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(response.json(), {'project': ['This field is required.']})

        # create contributor without user
        response = self.client.post("/contributors/", data={
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(response.json(), {'user': ['This field is required.']})

    # RETREIVE
    def test_get_contributor_from_author(self):

        self.client.force_login(self.project_author)

        response = self.client.get("/contributors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

        response = self.client.get("/contributors/1/")
        self.assertEqual(response.status_code, 200)

    def test_get_contributor_from_contributor(self):

        self.client.force_login(self.project_contributor)

        response = self.client.get("/contributors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

        response = self.client.get("/contributors/1/")
        self.assertEqual(response.status_code, 200)

    def test_get_contributor_from_unauthorized(self):

        # get contributors from non authenticated user
        response = self.client.get("/contributors/")
        self.assertEqual(response.status_code, 403)

        response = self.client.get("/contributors/1/")
        self.assertEqual(response.status_code, 403)

        # get contributors from non contributor user
        self.client.force_login(self.random_user)

        response = self.client.get("/contributors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get("/contributors/1/")
        self.assertEqual(response.status_code, 404)

    # UPDATE
    def test_update_contributor(self):

        # update from non authenticated user
        response = self.client.post("/contributors/1/", data={
            "user": self.random_user.pk
        })
        self.assertEqual(response.status_code, 403, response.json())

        # update from a non contributor user
        self.client.force_login(self.random_user)
        response = self.client.post("/contributors/1/", data={
            "user": self.random_user.pk
        })
        self.assertEqual(response.status_code, 405, response.json())

        # update from a contributor user
        self.client.force_login(self.project_contributor)
        response = self.client.post("/contributors/1/", data={
            "user": self.random_user.pk
        })
        self.assertEqual(response.status_code, 405, response.json())

        # update from a the project author
        self.client.force_login(self.project_author)
        response = self.client.post("/contributors/1/", data={
            "user": self.random_user.pk
        })
        self.assertEqual(response.status_code, 405, response.json())

    # DELETE
    def test_delete_contributor_from_author(self):

        self.client.force_login(self.project_author)

        response = self.client.delete("/contributors/1/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Contributor.objects.filter(pk=1).exists())

    def test_delete_contributor_from_unauthorized(self):

        # delete from a non authenticated user
        response = self.client.delete("/contributors/1/")
        self.assertEqual(response.status_code, 403)

        # delete from a contributor user
        self.client.force_login(self.project_contributor)

        response = self.client.delete("/contributors/1/")
        self.assertEqual(response.status_code, 403)

        # delete from a non contributor user
        self.client.force_login(self.project_contributor)

        response = self.client.delete("/contributors/1/")
        self.assertEqual(response.status_code, 403)
