# ideal_completion.py

from django import forms
from .models import Task, Attachment
from django.core.exceptions import ValidationError


# Utility function to clean attachments
def validate_attachment_extension(attachment):
    if not attachment.name.endswith(('.jpg', '.png')):
        raise ValidationError('Only JPG and PNG files are allowed')
    return attachment


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class TaskForm(forms.ModelForm):
    attachments = MultipleFileField()

    class Meta:
        model = Task
        fields = ('name', 'comments')

    def clean_attachments(self):
        attachments = self.files['attachments']
        for attachment in attachments:
            validate_attachment_extension(attachment)
        return attachments


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ('attachment',)

    def clean_attachment(self):
        attachment = self.cleaned_data['attachment']
        return validate_attachment_extension(attachment)
