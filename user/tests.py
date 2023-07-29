from rest_framework.test import APITestCase
from user.models import SoftdeskUser
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta


PASSWORD = "password"


class TestSoftdeskUser(APITestCase):

    def setUp(self) -> None:

        self.user = SoftdeskUser.objects.create_user(
            can_data_be_shared=False,
            can_be_contacted=False,
            username="admin",
            password=PASSWORD,
            age=27,
        )

    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(user)}')

    # CREATE
    def test_register(self):

        response = self.client.post("/register/", data={
            "can_data_be_shared": False,
            "can_be_contacted": False,
            "username": "new_user",
            "password": PASSWORD,
            "age": 25,
        })

        self.assertEqual(response.status_code, 201, response.json())
        self.assertTrue(SoftdeskUser.objects.filter(username="new_user").exists())

        response = self.client.post("/api/token/", data={
            "username": "new_user",
            "password": PASSWORD,
        })

        self.assertEqual(response.status_code, 200, response.json())
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def register_under_15_years_old(self):

        response = self.client.post("/register/", data={
            "username": "new_user",
            "password": PASSWORD,
            "age": 12
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'age': ['User must be at least 15 years old.']})

    def register_with_missing_datas(self):

        # register without username
        response = self.client.post("/register/", data={
            "password": PASSWORD,
            "age": 12
        })
        self.assertEqual(response.status_code, 400)

        # register without password
        response = self.client.post("/register/", data={
            "username": "new_user",
            "age": 25
        })
        self.assertEqual(response.status_code, 400)

        # register without age
        response = self.client.post("/register/", data={
            "username": "new_user",
            "password": PASSWORD,
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_unauthorized(self):

        # create user from non authenticated user
        response = self.client.post("/users/", data={
            "username": "new_user",
            "password": PASSWORD,
            "age": 25
        })
        self.assertEqual(response.status_code, 401)

        # create user from authenticated user
        self.authenticate(self.user)
        response = self.client.post("/users/", data={
            "username": "new_user",
            "password": PASSWORD,
            "age": 25
        })
        self.assertEqual(response.status_code, 405)

    # RETREIVE
    def test_get_users(self):

        self.authenticate(self.user)

        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/users/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], "admin")

        self.assertEqual(len(response.json()), 5)
        self.assertIn("can_be_contacted", response.json())
        self.assertIn("can_data_be_shared", response.json())
        self.assertIn("username", response.json())
        self.assertIn("age", response.json())
        self.assertIn("id", response.json())

    def test_get_user_from_non_authenticated(self):

        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 401)

        response = self.client.get("/users/1/")
        self.assertEqual(response.status_code, 401)

    # UPDATE
    def test_update_user(self):

        self.authenticate(self.user)

        response = self.client.patch("/users/1/", data={
            "can_data_be_shared": True,
            "can_be_contacted": True,
        })

        updated_user: SoftdeskUser = SoftdeskUser.objects.get(pk=1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.can_data_be_shared, True)
        self.assertEqual(updated_user.can_be_contacted, True)

    def test_update_user_from_unauthorized(self):

        user: SoftdeskUser = SoftdeskUser.objects.create(
            can_data_be_shared=False,
            can_be_contacted=False,
            username="new_user",
            password=PASSWORD,
            age=27,
        )

        # update user from non authenticated user
        response = self.client.patch(f"/users/{user.pk}/", data={
            "can_data_be_shared": True,
            "can_be_contacted": True,
        })
        self.assertEqual(response.status_code, 401)

        # update user from another user
        self.authenticate(self.user)
        response = self.client.patch(f"/users/{user.pk}/", data={
            "can_data_be_shared": True,
            "can_be_contacted": True,
        })
        self.assertEqual(response.status_code, 403)

        self.assertEqual(user.can_data_be_shared, False)
        self.assertEqual(user.can_be_contacted, False)

    # DELETE
    def test_delete_user(self):

        self.authenticate(self.user)

        response = self.client.delete(f"/users/{self.user.pk}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(SoftdeskUser.objects.filter(username=self.user.username).exists())

    def test_delete_user_from_unauthorized(self):

        user: SoftdeskUser = SoftdeskUser.objects.create(
            can_data_be_shared=False,
            can_be_contacted=False,
            username="new_user",
            password=PASSWORD,
            age=27,
        )

        # update user from non authenticated user
        response = self.client.delete(f"/users/{user.pk}/")
        self.assertEqual(response.status_code, 401)

        # update user from another user
        self.authenticate(self.user)
        response = self.client.patch(f"/users/{user.pk}/")
        self.assertEqual(response.status_code, 403)

        self.assertTrue(SoftdeskUser.objects.filter(pk=user.pk).exists())


class TestAuthentification(APITestCase):

    def setUp(self) -> None:

        self.user = SoftdeskUser.objects.create_user(
            username="user",
            password=PASSWORD,
            age=27,
        )

    def test_get_access_token_with_valid_credential(self):

        response = self.client.post("/api/token/", data={
            "username": self.user.username,
            "password": PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_get_access_token_with_invalid_credential(self):

        response = self.client.post("/api/token/", data={
            "username": self.user.username,
            "password": "invalid_password",
        })

        self.assertEqual(response.status_code, 401)

    def test_token_expiration(self):

        expired_token = AccessToken.for_user(self.user)
        expired_token.set_exp(lifetime=-timedelta(hours=1))

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 401, response.json())
        self.assertEqual(response.json()['detail'], 'Given token not valid for any token type')

    def test_refresh_access_token(self):

        # get a first token
        response = self.client.post("/api/token/", data={
            "username": self.user.username,
            "password": PASSWORD,
        })

        access_token = response.json()['access']
        refresh_token = response.json()['refresh']

        response = self.client.post(
            path="/api/token/refresh/",
            headers={
                'Authorization': f'Bearer {access_token}',
            },
            data={
                "refresh": refresh_token
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue("access" in response.json())
