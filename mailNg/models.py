from django.contrib.auth.models import User
from django.db import models

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ng_emails")
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name="ng_emails_sent")
    recipients = models.ManyToManyField(User, related_name="ng_emails_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "recipients": [user.username for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%d/%m/%y %H:%M"),
            "read": self.read,
            "archived": self.archived
        }

    def __str__(self):
        return f'{self.user.username} mailbox: email {self.id} "{self.subject}"'
