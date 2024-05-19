from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from chat.models import Thread, Message
from chat.pagination import DefaultSetPagination
from chat.serializers import ThreadSerializer, MessageSerializer, MessageReadSerializer


@extend_schema(
    tags=['Chat, Threads'],
    summary='Create a new thread',
    description='Endpoint to create a new thread.'
)
class ThreadCreateView(CreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]
    queryset = Thread.objects.all()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participants_ids = serializer.data['participants']
        participants = User.objects.filter(id__in=participants_ids).all()

        if request.user not in participants:
            message = 'One of participants must be user that made request.'
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

        existing_thread = Thread.objects.filter(participants__in=participants)
        for p in participants:
            existing_thread = existing_thread.filter(participants=p)

        if existing_thread.exists():
            thread = existing_thread.first()
            response_status = status.HTTP_200_OK
        else:
            thread = Thread.objects.create()
            thread.participants.add(*participants)
            response_status = status.HTTP_201_CREATED

        serializer = self.get_serializer(thread)

        return Response(serializer.data, status=response_status)


@extend_schema(
    tags=['Chat, Threads'],
    summary='Delete a thread',
    description='Endpoint to delete a thread by ID.'
)
class ThreadDestroyView(DestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)  # User can only delete his own threads


@extend_schema(
    tags=['Chat, Threads'],
    summary='Get user threads',
    description='Endpoint to get users threads.'
)
class ThreadListView(ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)  # User can get only his own threads


@extend_schema(
    tags=['Chat, Messages'],
    summary='Create a new message in thread',
    description='Endpoint to create a new message in thread.'
)
class MessageCreateView(CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thread = serializer.validated_data['thread']

        if request.user not in thread.participants.all():
            message = 'You do not have permission to post in this thread.'
            self.permission_denied(self.request, message=message)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=['Chat, Messages'],
    summary='Get thread messages',
    description='Endpoint to get thread messages.'
)
class MessageListView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultSetPagination

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        thread = get_object_or_404(Thread, id=thread_id)

        if self.request.user not in thread.participants.all():
            message = 'You do not have permission to access messages in this thread.'
            self.permission_denied(self.request, message=message)

        return Message.objects.filter(thread=thread).order_by('created')


@extend_schema(
    tags=['Chat, Messages'],
    summary='Change message read status',
    description='Endpoint to change message read status.'
)
class MessageReadChangeView(UpdateAPIView):
    serializer_class = MessageReadSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    queryset = Message.objects.all()

    def update(self, request, *args, **kwargs):
        message = self.get_object()

        if request.user not in message.thread.participants.all():
            message = 'You do not have permission to mark this message as read.'
            self.permission_denied(self.request, message=message)

        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Chat, Messages'],
    summary='Get unread messages count',
    description='Endpoint to get unread messages count for all user threads.'
)
class UnreadMessageCountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        unread_count = Message.objects.filter(thread__participants=user, is_read=False).exclude(sender=user).count()
        return Response({'unread_messages_count': unread_count}, status=status.HTTP_200_OK)
