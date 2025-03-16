from rest_framework import serializers
from .models import Document, Chat, Message

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'vectorstore_path')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'content', 'is_user', 'created_at']
        read_only_fields = ('created_at',)

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'title', 'messages', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None 