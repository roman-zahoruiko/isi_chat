from django.urls import path
from chat.views import (
    ThreadCreateView, ThreadDestroyView, ThreadListView,
    MessageCreateView, MessageListView, MessageReadChangeView, UnreadMessageCountView
)

urlpatterns = [
    # threads
    path('threads/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<int:pk>/delete/', ThreadDestroyView.as_view(), name='thread_destroy'),
    path('threads/list/', ThreadListView.as_view(), name='thread_list'),
    # messages
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('threads/<int:thread_id>/messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/<int:pk>/read/', MessageReadChangeView.as_view(), name='message_read_change'),
    path('messages/unread/', UnreadMessageCountView.as_view(), name='unread_messages_count'),
]
