from rest_framework import serializers
from chat.models import Thread, Message


class ThreadSerializer(serializers.ModelSerializer):

    def validate_participants(self, values):
        if len(values) != 2:
            raise serializers.ValidationError(f'A thread must have only 2 participants.')
        if len(values) != len(set(values)):
            raise serializers.ValidationError(f'The participant duplicated.')
        return values

    class Meta:
        model = Thread
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'thread', 'created', 'is_read']
        read_only_fields = ['id', 'sender', 'created', 'is_read']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['sender'] = request.user
        return super().create(validated_data)


class MessageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['is_read']
