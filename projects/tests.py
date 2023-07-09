from rest_framework.test import APITestCase
from user.models import SoftdeskUser
from projects.models import Project, Contributor


class TestProject(APITestCase):

    def setUp(self) -> None:

        self.admin = SoftdeskUser.objects.create_user(
            username="admin",
            password="password",
            age=27,
        )

        self.end_user = SoftdeskUser.objects.create_user(
            username="end_user",
            password="password",
            age=27,
        )

        self.client.force_login(self.admin)
        self.client.post("/projects/", data={
            "description": "existing_project",
            "type": "FRONT",
            "author": self.admin.pk
        })

    def test_get_project(self):

        # get all projects
        response = self.client.get("/projects/")

        # assert data have been successfully received
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_get_project_without_credential(self):

        # logout the authenticated user in setUp() method
        self.client.logout()

        # assert that access is denied
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 403)

    def test_create_project(self):
        """
        Create a new project, with user created in setUp() as author
        """

        # create new project
        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "FRONT",
            "author": self.end_user.pk
        })

        # check the status code of the response
        self.assertIn(response.status_code, [200, 201], response.json())

        # read the created project from the database
        project = Project.objects.get(description="new_project")

        # check that the created project has good attributes
        self.assertEqual(project.description, "new_project")
        self.assertEqual(project.type, "FRONT")
        self.assertEqual(project.author.username, "end_user")

        # retreive the created project from the api endpoint
        response = self.client.get("/projects/?description=new_project")

        self.assertIn(response.status_code, [200, 201], response.json())
        self.assertEqual(response.json()['count'], 1)

        # assert the author was added to the contributors table
        contributor = Contributor.objects.filter(project_id=project.pk, user_id=self.end_user.pk)
        self.assertTrue(contributor.exists())

    def test_create_project_without_author(self):

        # create new project without specifiying author
        response = self.client.post("/projects/", data={
            "description": "Dummy description",
            "type": "FRONT",
        })

        # assert that the request was rejected
        self.assertIn(response.status_code, [400], response.json())

    def test_create_project_with_invalid_type(self):

        # create new project with invalid type
        response = self.client.post("/projects/", data={
            "description": "new_project",
            "type": "Invalid type",
            "author": self.end_user.pk
        })

        # check the status code of the response
        self.assertEqual(response.status_code, 400, response.json())

    def test_update_project(self):

        # update the existing project, created in setUp() method
        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        # assert update was sucessfully applied
        self.assertIn(response.status_code, [200, 201])

        # retreive the project from django ORM
        project = Project.objects.get(description="existing_project")

        # assert the update was sucessfully applied in database
        self.assertEqual(project.type, "BACK")

    def test_update_project_from_non_author(self):

        # logout the author of the project 1
        self.client.logout()

        # login a user who is not the author or project 1
        self.client.force_login(self.end_user)

        # try to update project 1 from non author account
        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        # assert the update operation as rejected
        self.assertEqual(response.status_code, 403)

    def test_delete_project(self):

        PROJECT_DESC = "existing_project"

        # check if the project we want to delete exists
        existing_project = Project.objects.filter(description=PROJECT_DESC)
        self.assertTrue(existing_project.exists())

        # delete the desired project
        response = self.client.delete("/projects/1/")
        self.assertEqual(response.status_code, 204)

        # check if the desired project was successfully deleted
        deleted_project = Project.objects.filter(description=PROJECT_DESC)
        self.assertFalse(deleted_project.exists())

    def test_delete_project_from_non_author(self):

        # logout the author of project 1
        self.client.logout()

        # login a user who is not the author of project 1
        self.client.force_login(self.end_user)

        # try to delete the project 1 from non author
        response = self.client.delete("/projects/1/")

        # assert the delete operation was rejected
        self.assertEqual(response.status_code, 403)


class TestContributor(APITestCase):

    def setUp(self) -> None:

        self.authenticated_user = SoftdeskUser.objects.create(
            username="end_user",
            password="admin",
            age=27
        )
        self.client.force_login(self.authenticated_user)

        self.author1 = SoftdeskUser.objects.create(
            username="author1",
            password="admin",
            age=27
        )

        self.project1 = Project.objects.create(
            description="project1",
            type="FRONT",
            author=self.author1
        )

        self.author2 = SoftdeskUser.objects.create(
            username="author2",
            password="admin",
            age=27
        )

        self.project2 = Project.objects.create(
            description="project2",
            type="BACK",
            author=self.author2
        )

        self.assertEqual(
            Contributor.objects.all().count(),
            2
        )

    def test_get_contributor(self):

        response = self.client.get("/contributors/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_get_contributor_without_credential(self):

        self.client.logout()

        response = self.client.get("/contributors/")

        self.assertEqual(response.status_code, 403)

    def test_create_contributor(self):

        response = self.client.post("/contributors/", data={
            "user": 3,
            "project": 1,
        })

        self.assertEqual(response.status_code, 201)

        contributor = Contributor.objects.get(pk=3)

        self.assertEqual(contributor.project.description, "project1")
        self.assertEqual(contributor.user.username, "author2")

    def test_create_existing_contributor(self):

        response = self.client.post("/contributors/", data={
            "user": 2,
            "project": 1,
        })

        self.assertEqual(response.status_code, 400, response.json())

    def test_update_contributor(self):

        response = self.client.post("/contributors/1/", data={
            "user": 3
        })

        self.assertEqual(response.status_code, 405, response.json())

    def test_delete_contributor(self):

        self.client.logout()
        self.client.force_login(self.author1)

        response = self.client.delete("/contributors/1/")

        self.assertEqual(response.status_code, 204)

    def test_delete_contributor_without_being_author(self):

        response = self.client.get("/contributors/1/")

        # assert that the desired project author is different to logged author
        self.assertEqual(response.json()['project']['author']['username'], "author1")

        # try to delete a contributor from a project, without being registered as the author of this project
        response = self.client.delete("/contributors/1/")

        self.assertEqual(response.status_code, 403)
