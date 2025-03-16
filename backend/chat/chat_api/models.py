from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    vectorstore_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'chat_api'
        db_table = 'chat_document'

class Chat(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'chat_api'
        db_table = 'chat_chat'

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'User' if self.is_user else 'Assistant'} - {self.content[:50]}"

    class Meta:
        ordering = ['created_at']
        app_label = 'chat_api'
        db_table = 'chat_message'