import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from network.models import User


class LoginAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User(name='boy', email='boy@gmail.com', password='boyboy1375')
        self.user.save()

    def test_successful_login(self):
        payload = {
            'email': self.user.email,
            'password': self.user.password
        }
        resp = self.client.post(reverse('api-v1:login'),
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_incorrect_password(self):
        payload = {
            'email': self.user.email,
            'password': 'badboy'
        }
        resp = self.client.post(reverse('api-v1:login'),
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)