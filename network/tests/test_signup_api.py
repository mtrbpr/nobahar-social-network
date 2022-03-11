import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from network.models import User


class SignupAPITestCase(APITestCase):

    def test_successful_signup(self):
        payload = {
          "name": "Mohsen",
          "email": "test@gmail.com",
          "password": "12345678@"
        }

        resp = self.client.post(reverse('api-v1:signup'),
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.all().exists())
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['message'], 'successfull')

    def test_signup_fails_for_duplicate_email(self):
        user = User(name='boy', email='boy@gmail.com', password='boyboy1375')
        user.save()

        payload = {
            "name": "Mohsen",
            "email": "boy@gmail.com",
            "password": "12345678@"
        }

        resp = self.client.post(reverse('api-v1:signup'),
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {
          "error": {
            "enMessage": "Bad request!"
          }
        })

    def test_signup_fails_for_invalid_password(self):
        payload = {
            "name": "Mohsen",
            "email": "test@gmail.com",
            "password": ""
        }

        resp = self.client.post(reverse('api-v1:signup'),
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {
            "error": {
                "enMessage": "Bad request!"
            }
        })