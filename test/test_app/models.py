from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Attachment(models.Model):
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/')

    def __str__(self):
        return self.attachment.name
