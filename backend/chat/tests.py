from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from chat.models import Thread, Message


class ChatAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')

        self.thread = Thread.objects.create()
        self.thread.participants.set([self.user1, self.user2])

        self.message = Message.objects.create(
            sender=self.user1,
            text='Hello',
            thread=self.thread
        )

        self.token_url = reverse('api_token_auth')
        # Thread endpoints
        self.thread_create_url = reverse('thread_create')
        self.thread_delete_url = reverse('thread_delete', kwargs={'pk': self.thread.id})
        self.thread_list_url = reverse('thread_list')
        # Message endpoints
        self.message_create_url = reverse('message_create')
        self.message_list_url = reverse('messages_list', kwargs={'thread_id': self.thread.id})
        self.message_read_url = reverse('message_read_change', kwargs={'pk': self.message.id})
        self.unread_message_count_url = reverse('unread_messages_count')

        # Get token for user1
        response = self.client.post(self.token_url, {'username': 'user1', 'password': 'password'}, format='json')
        self.token = response.data['token']

    def test_anonymous_access(self):
        urls = [
            self.thread_create_url,
            self.thread_delete_url,
            self.thread_list_url,
            self.message_create_url,
            self.message_list_url,
            self.message_read_url,
            self.unread_message_count_url,
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_thread_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.post(self.thread_create_url,
                                    {'participants': [self.user1.pk, self.user3.pk]},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_thread_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.get(self.thread_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.post(self.message_create_url, {
            'sender': self.user1.id,
            'text': 'New message',
            'thread': self.thread.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_message_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.get(self.message_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_read(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.patch(self.message_read_url, {'is_read': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_count(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.get(self.unread_message_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_destroy(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.delete(self.thread_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
