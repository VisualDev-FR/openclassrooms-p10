from rest_framework.test import APITestCase
from user.models import SoftdeskUser
from projects.models import Project


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

        response = self.client.get("/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_get_project_without_credential(self):

        self.client.logout()

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

        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

        self.assertIn(response.status_code, [200, 201])

        project = Project.objects.get(description="existing_project")

        self.assertEqual(project.type, "BACK")

    def test_update_project_from_non_author(self):

        self.client.logout()
        self.client.force_login(self.end_user)

        response = self.client.patch("/projects/1/", data={
            "type": "BACK",
        })

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

        self.client.logout()
        self.client.force_login(self.end_user)

        response = self.client.delete("/projects/1/")

        self.assertEqual(response.status_code, 403)
