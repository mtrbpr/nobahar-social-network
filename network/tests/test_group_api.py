import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from network.models import User, Group


class GroupAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User(name='boy', email='boy@gmail.com', password='boyboy1375')
        self.user.save()
        self.client.force_authenticate(self.user)

    def test_post_group(self):
        payload = {
          "name": "Gank of four",
          "description": "We are here for design ..."
        }

        resp = self.client.post(reverse('api-v1:groups-list'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(Group.objects.all().exists())
        self.assertTrue(self.user.group)
        self.assertEqual(resp.data, {
          "group": {
            "id": str(self.user.group.id)
          },
          "message": "successfull"
        })

    def test_post_group_fails_for_user_that_already_has_group(self):
        group = Group(name='boy', description='boy desc')
        group.owner = self.user
        group.save()
        self.user.group = group
        self.user.save()

        payload = {
            "name": "Gank of four",
            "description": "We are here for design ..."
        }
        resp = self.client.post(reverse('api-v1:groups-list'),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_group_controller(self):
        group = Group(name='boy', description='boy desc')
        group.owner = self.user
        group.save()
        self.user.group = group
        self.user.save()

        resp = self.client.get(reverse('api-v1:groups-my'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['group']['members']), 1)

    def test_when_user_has_no_group_my_should_return_400(self):
        resp = self.client.get(reverse('api-v1:groups-my'))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)