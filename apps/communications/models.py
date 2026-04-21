# communication/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):

    TARGET_CHOICES = [
        ('all_students', 'All Students'),
        ('all_trainees', 'All Trainees'),
        ('all_schools', 'All Schools'),

        ('school_students', 'School Students'),
        ('class_students', 'Class Students'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('important', 'Important'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')

    title = models.CharField(max_length=255)
    content = models.TextField()

    target_type = models.CharField(max_length=50, choices=TARGET_CHOICES)

    # Optional targeting filters
    school = models.ForeignKey('schools.School', null=True, blank=True, on_delete=models.CASCADE)
    section = models.ForeignKey('schools.Section', null=True, blank=True, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.sender}"
    
    
    
class Notification(models.Model):

    TYPE_CHOICES = [
        ('message', 'Message'),
        ('system', 'System'),
        ('result', 'Result'),
        ('payment', 'Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')

    title = models.CharField(max_length=255)
    content = models.TextField()

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='message')

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title}"
    
    
    
class Device(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')

    device_token = models.TextField()

    device_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web'),
            ('android', 'Android'),
            ('ios', 'iOS')
        ],
        default='web'
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.device_type}"
    
    
class MessageReadStatus(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'message')
        
        
        
class MessageAttachment(models.Model):

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')

    file = models.FileField(upload_to='message_attachments/')

    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    
    
# apps/communications/models.py
class Conversation(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)