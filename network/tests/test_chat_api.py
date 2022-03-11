import json
from random import randint

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from network.models import User, Group, ConnectionRequest, ChatMessage


class ChatAPITestCase(APITestCase):

    @staticmethod
    def mock_user_and_group():
        salt = randint(1000, 9999)
        user1 = User(name=f'boy{salt}', email=f'b{salt}oy@gmail.com',
                     password=f'boy{salt}boy1375')
        user1.save()
        group1 = Group(name=f'bdsf{salt}oy', description=f'boy {salt}desc')
        group1.owner = user1
        group1.save()
        user1.group = group1
        user1.save()
        return user1, group1

    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = User(name='boy', email='boy@gmail.com', password='boyboy1375')
        self.user2 = User(name='gurl', email='gurl@gmail.com', password='bgurloy1375')
        self.user1.save()
        self.user2.save()
        self.group = Group(name='boy', description='boy desc')
        self.group.owner = self.user1
        self.group.save()
        self.user1.group = self.group
        self.user2.group = self.group
        self.user1.save()
        self.user2.save()

    def test_people_in_same_group_can_chat(self):
        self.client.force_authenticate(self.user1)
        payload = {
            'message': 'some boy message'
        }
        resp = self.client.post(reverse('api-v1:chats', kwargs={'user_id': self.user2.id}),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(ChatMessage.objects.all().exists())

    def test_people_in_different_groups_can_not_chat(self):
        self.client.force_authenticate(self.user1)
        user3, group3 = self.mock_user_and_group()

        payload = {
            'message': 'some boy message'
        }
        resp = self.client.post(reverse('api-v1:chats', kwargs={'user_id': user3.id}),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_people_in_different_groups_but_connected_can_chat(self):
        self.user1, self.group1 = self.mock_user_and_group()
        self.user2, self.group2 = self.mock_user_and_group()
        cr = ConnectionRequest(requester=self.group1, requestee=self.group2, accepted=True)
        cr.save()

        self.client.force_authenticate(self.user1)

        payload = {
            'message': 'some boy message'
        }

        resp = self.client.post(reverse('api-v1:chats', kwargs={'user_id': self.user2.id}),
                                data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_chat(self):
        cm = ChatMessage(user_from=self.user2, user_to=self.user1, message='boy')
        cm.save()
        self.client.force_authenticate(self.user1)
        resp = self.client.get(reverse('api-v1:chats', kwargs={'user_id': self.user2.id}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('messages', resp.data)

    def test_get_all_chats(self):
        cm = ChatMessage(user_from=self.user2, user_to=self.user1, message='boy')
        cm.save()
        self.client.force_authenticate(self.user1)
        resp = self.client.get(reverse('api-v1:chats-all'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
