import json
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from network.models import User, Group, ConnectionRequest


class ConnectionRequestAPITestCase(APITestCase):

    @staticmethod
    def mock_user_and_group():
        salt = random.randint(1000, 9999)
        user1 = User(name=f'boy{salt}', email=f'b{salt}oy@gmail.com',
                     password=f'boy{salt}boy1375')
        user1.save()
        group1 = Group(name=f'bdsf{salt}oy', description=f'boy {salt}desc')
        group1.owner = user1
        group1.save()
        user1.group = group1
        user1.save()
        return user1, group1

    def setUp(self):
        self.client = APIClient()
        self.user1, self.group1 = self.mock_user_and_group()
        self.user2, self.group2 = self.mock_user_and_group()
        self.client.force_authenticate(self.user1)

    def test_post_connection_request(self):
        payload = {
            "groupId": self.group2.id
        }
        resp = self.client.post(reverse('api-v1:connection_requests-list'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(ConnectionRequest.objects.all().exists())
        cr = ConnectionRequest.objects.first()
        self.assertEqual(cr.requester, self.group1)
        self.assertEqual(cr.requestee, self.group2)

    def test_get_connection_request(self):
        cr = ConnectionRequest(requester=self.group1, requestee=self.group2)
        cr.save()
        self.client.force_authenticate(self.user2)
        resp = self.client.get(reverse('api-v1:connection_requests-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('requests', resp.data)
        cr_res = resp.data['requests'][0]
        self.assertEqual(cr.id, cr_res['connectionRequestId'])
        self.assertEqual(cr.requester.id, cr_res['groupId'])
        self.assertEqual(cr.date.timestamp(), cr_res['sent'])

    def test_accept_connection_request(self):
        cr = ConnectionRequest(requester=self.group1, requestee=self.group2)
        cr.save()
        self.client.force_authenticate(self.user2)
        payload = {
            "groupId": self.group1.id
        }
        resp = self.client.post(reverse('api-v1:connection_requests-accept'), data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

