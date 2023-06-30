from rest_framework.test import APITestCase
from user.models import SoftdeskUser


class TestSoftdeskUser(APITestCase):

    url = "/users/"

    def setUp(self) -> None:
        self.user = SoftdeskUser.objects.create_user(
            username="admin",
            password="password",
            age=27,
        )

        self.client.force_login(self.user)

    def test_get_user(self):
        """
        Read the user created in TestSoftdeskUser.setUp()
        """
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["count"], 1, data)
        self.assertEqual(data["results"][0]["username"], "admin", data)

    def test_create_user(self):
        """
        Create a valid user and assert that response is correct, and data are correclty written in database
        """

        self.assertFalse(SoftdeskUser.objects.filter(username="new_user").exists())

        response = self.client.post(self.url, data={
            "username": "new_user",
            "password": "password",
            "age": 15,
        })

        self.assertIn(response.status_code, [200, 201], response.json())
        self.assertNotEqual(SoftdeskUser.objects.get(username="new_user"), None)

    def test_create_user_under_15_years_old(self):
        """
        Check that no user under 15 years old can be created
        """

        self.assertFalse(SoftdeskUser.objects.filter(username="new_user").exists())

        response = self.client.post(self.url, data={
            "username": "new_user",
            "password": "password",
            "age": 12,
        })

        self.assertEqual(response.status_code, 400, response.json())
        self.assertFalse(SoftdeskUser.objects.filter(username="new_user").exists())
