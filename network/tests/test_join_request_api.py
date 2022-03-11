import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from network.models import User, Group, JoinRequest


class JoinRequestAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User(name='boy', email='boy@gmail.com', password='boyboy1375')
        self.user.save()
        self.group = Group(name='boy', description='boy desc')
        self.group.owner = self.user
        self.group.save()
        self.user.group = self.group
        self.user.save()
        self.user2 = User(name='girl', email='girl@gmail.com', password='girlgirl1375')
        self.user2.save()
        self.client.force_authenticate(self.user2)

    def test_post_join_request(self):
        payload = {
          "groupId": self.group.id
        }
        resp = self.client.post(reverse('api-v1:join_requests-list'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
          "message": "successfull"
        })
        self.assertEqual(len(JoinRequest.objects.all()), 1)

    def test_post_for_user_that_already_has_group_should_fail(self):
        self.client.force_authenticate(self.user)
        payload = {
            "groupId": self.group.id
        }
        resp = self.client.post(reverse('api-v1:join_requests-list'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {
          "error": {
            "enMessage": "Bad request!"
          }
        })

    def test_get_join_request(self):
        self.client.force_authenticate(self.user2)
        join_request = JoinRequest(group=self.group, user=self.user2)
        join_request.save()

        resp = self.client.get(reverse('api-v1:join_requests-list'))
        self.assert_join_request(join_request, resp)

    def assert_join_request(self, join_request, resp):
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("joinRequests", resp.data)
        jr = resp.data['joinRequests'][0]
        self.assertEqual(jr['id'], join_request.id)
        self.assertEqual(jr['groupId'], join_request.group.id)
        self.assertEqual(jr['userId'], join_request.user.id)
        self.assertEqual(jr['date'], join_request.date.timestamp())

    def test_get_join_requests_to_user_group(self):
        self.client.force_authenticate(self.user)
        join_request = JoinRequest(group=self.group, user=self.user2)
        join_request.save()

        resp = self.client.get(reverse('api-v1:join_requests-group'))
        self.assert_join_request(join_request, resp)

    def test_only_owner_can_get_join_requests_to_user_group(self):
        self.user2.group = self.group
        self.user2.save()
        self.client.force_authenticate(self.user2)

        resp = self.client.get(reverse('api-v1:join_requests-group'))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {
            "error": {
                "enMessage": "Bad request!"
            }
        })

    def test_accept_join_request(self):
        join_request = JoinRequest(group=self.group, user=self.user2)
        join_request.save()
        self.client.force_authenticate(self.user)

        payload = {
            "joinRequestId": join_request.id
        }
        self.assertFalse(self.user2.group)
        resp = self.client.post(reverse('api-v1:join_requests-accept'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.group, join_request.group)

    def test_normal_user_can_not_accept_join_requests(self):
        join_request = JoinRequest(group=self.group, user=self.user2)
        join_request.save()
        self.client.force_authenticate(self.user2)
        payload = {
            "joinRequestId": join_request.id
        }
        resp = self.client.post(reverse('api-v1:join_requests-accept'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_join_request_fails_when_user_is_already_joined_to_another_group(self):
        join_request = JoinRequest(group=self.group, user=self.user2)
        join_request.save()
        self.user2.group = self.group
        self.user2.save()
        self.client.force_authenticate(self.user)
        payload = {
            "joinRequestId": join_request.id
        }
        resp = self.client.post(reverse('api-v1:join_requests-accept'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
