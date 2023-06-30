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

    def test_create_user(self):

        response = self.client.post(self.url, data={
            "username": "new_user",
            "password": "password",
            "age": 15,
        })

        self.assertIn(response.status_code, [200, 201], response.json())
        self.assertNotEqual(SoftdeskUser.objects.get(username="new_user"), None)

    def test_create_user_less_than_15_years_old(self):

        response = self.client.post(self.url, data={
            "username": "new_user",
            "password": "password",
            "age": 12,
        })

        self.assertEqual(response.status_code, 400, response.json())
        self.assertFalse(SoftdeskUser.objects.filter(username="new_user").exists())
