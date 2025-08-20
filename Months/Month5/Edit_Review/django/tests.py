import os
import re
import shutil
import unittest
import atexit
import django

from pylint import lint
from django.core.management import call_command

COMPLETION_FILE = "ideal_completion.py"

SETTINGS = """from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-xxx'
DEBUG = True

ROOT_URLCONF = 'test_project.urls'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

INSTALLED_APPS = [
    'test_app.apps.TestAppConfig',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True
"""

MODELS_FILE_CONTENT = """from django.db import models

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
"""

TEST_APP = """from django.apps import AppConfig

class TestAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_app'
"""


# Ensure the 'test_app' and 'settings.py' files exist and load them dynamically
def setup_django_project():
    if not os.path.exists('test_project'):
        os.makedirs('test_project')

        with open('test_project/settings.py', 'w') as f:
            f.write(SETTINGS)

    # Create the test app folder if it doesn't exist
    if not os.path.exists('test_app'):
        os.makedirs('test_app')
        os.makedirs('test_app/migrations')
        with open('test_app/__init__.py', 'w') as f:
            pass
        with open('test_app/migrations/__init__.py', 'w') as f:
            pass
        with open('test_app/apps.py', 'w') as f:
            f.write(TEST_APP)
        with open('test_app/models.py', 'w') as f:
            f.write(MODELS_FILE_CONTENT)

        shutil.copy(COMPLETION_FILE, 'test_app/forms.py')

    # Load settings programmatically
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()

    call_command('makemigrations', 'test_app', verbosity=2)
    call_command('migrate', verbosity=2)

setup_django_project()

# Register cleanup on exit to ensure proper file removal
def cleanup():
    if os.path.exists('split'):
        shutil.rmtree('split')
    if os.path.exists('test_app'):
        shutil.rmtree('test_app')
    if os.path.exists('test_project'):
        shutil.rmtree('test_project')

atexit.register(cleanup)

from django.core.files.uploadedfile import SimpleUploadedFile
from test_app.forms import TaskForm, AttachmentForm


class TestAttachmentValidation(unittest.TestCase):
    # Test to ensure that the TaskForm is valid when valid attachments are provided (JPG and PNG files).
    def test_task_form_valid_attachments(self):
        form_data = {'name': 'Test Task', 'comments': 'Test comments'}
        file_data = {
            'attachments': [
                SimpleUploadedFile('test.jpg', b'test_content'),
                SimpleUploadedFile('image.png', b'test_content'),
            ]
        }
        form = TaskForm(data=form_data, files=file_data)
        is_valid = form.is_valid()
        print(form.errors)
        self.assertTrue(is_valid)  # The form should be valid since all attachments are allowed file types (JPG, PNG).

    # Test to ensure that the TaskForm is invalid when invalid attachments are provided (non-JPG/PNG files).
    def test_task_form_invalid_attachments(self):
        form_data = {'name': 'Test Task', 'comments': 'Test comments'}
        file_data = {
            'attachments': [
                SimpleUploadedFile('test.pdf', b'test_content'),
                SimpleUploadedFile('image.bmp', b'test_content'),
            ]
        }
        form = TaskForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())  # The form should be invalid since the attachments are not allowed (PDF, BMP).
        self.assertIn('attachments', form.errors)  # Check that the error is associated with the 'attachments' field.
        self.assertTrue('Only JPG and PNG files are allowed' in str(form.errors['attachments']))  # Specific error message validation.

    # Test to ensure that the AttachmentForm is valid when a valid attachment is provided (JPG file).
    def test_attachment_form_valid_attachment(self):
        file_data = {
            'attachment': SimpleUploadedFile('image.jpg', b'test_content'),
        }
        form = AttachmentForm(files=file_data)
        self.assertTrue(form.is_valid())  # The form should be valid because the attachment is an allowed type (JPG).

    # Test to ensure that the AttachmentForm is invalid when an invalid attachment is provided (non-JPG/PNG file).
    def test_attachment_form_invalid_attachment(self):
        file_data = {
            'attachment': SimpleUploadedFile('document.pdf', b'test_content'),
        }
        form = AttachmentForm(files=file_data)
        self.assertFalse(form.is_valid())  # The form should be invalid because the attachment is not an allowed type (PDF).
        self.assertIn('attachment', form.errors)  # Check that the error is associated with the 'attachment' field.
        self.assertTrue('Only JPG and PNG files are allowed' in str(form.errors['attachment']))  # Specific error message validation.

    # Test to check for duplicate code between the TaskForm and AttachmentForm, ensuring clean code structure.
    def test_duplicate_codes(self):
        # Ensure the split directory exists for separating TaskForm and AttachmentForm code.
        os.makedirs('split', exist_ok=True)

        # Read the content of the original file where both TaskForm and AttachmentForm are defined.
        with open(COMPLETION_FILE, 'r') as original_file:
            content = original_file.read()

        # Use regex to split the content before and after the AttachmentForm class to separate both forms.
        split_content = re.split(r'(\nclass AttachmentForm)', content)

        # First part: Everything before 'class AttachmentForm' which contains TaskForm code.
        task_form_content = split_content[0]

        # Second part: 'class AttachmentForm' and everything after it, which is the AttachmentForm code.
        attachment_form_content = ''.join(split_content[1:])

        # Write the TaskForm content to 'task_form.py' file in the split directory.
        with open('split/task_form.py', 'w') as task_form_file:
            task_form_file.write(task_form_content)

        # Write the AttachmentForm content to 'attachmentform.py' file in the split directory.
        with open('split/attachment_form.py', 'w') as attachment_form_file:
            attachment_form_file.write(attachment_form_content)

        # Pylint configuration to check for duplicate code across the split directory, focusing on similarities in the code.
        pylint_options = ['--disable=all', '--enable=similarities', '--min-similarity-lines=1', 'split/']

        # Run Pylint without stopping the script to detect any similarities in code.
        results = lint.Run(pylint_options, exit=False)

        # Ensure no duplicate code issues were detected.
        self.assertEqual(results.linter.msg_status, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

