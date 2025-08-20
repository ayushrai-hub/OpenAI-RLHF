
import os
import shutil
import unittest
import atexit
import django

from django.core.management import call_command

from yg import (
    MAIN_NAVIGATION_CONTENT,
    DECORATORS_CONTENT,
    SOME_MODULE_CONTENT,
    CONTEXT_PROCESSOR_CONTENT,
    TEMPLATES_CONTENT,
    MENU_TEMPLATE_CONTENT
)


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
"""

TEST_APP = """from django.apps import AppConfig

class TestAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_app'
    
    def ready(self):
        # Import the module to ensure it gets loaded
        import test_app.some_module
"""

TEST_APP_VIEWS = """
from django.shortcuts import render

def admin_menu_view(request):
    return render(request, 'menu.html')  # No need to specify the app in the template path
"""

TEST_APP_URLS = """from django.urls import path
from test_app.views import admin_menu_view

urlpatterns = [
    path('admin-menu/', admin_menu_view, name='admin-menu'),
]"""

URLS = """from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('test_app.urls')),  # Include the URLs from test_app
]
"""

# Ensure the 'test_app' and 'settings.py' files exist and load them dynamically
def setup_django_project():
    if not os.path.exists('test_project'):
        os.makedirs('test_project')

        with open('test_project/settings.py', 'w') as f:
            f.write(SETTINGS + TEMPLATES_CONTENT)
        with open('test_project/urls.py', 'w') as f:
            f.write(URLS)

    if not os.path.exists('templates'):
        os.makedirs('templates')

        with open('templates/menu.html', 'w') as f:
            f.write(MENU_TEMPLATE_CONTENT)

    # Create the test app folder if it doesn't exist
    if not os.path.exists('test_app'):
        os.makedirs('test_app/migrations')
        with open('test_app/__init__.py', 'w') as f:
            pass
        with open('test_app/migrations/__init__.py', 'w') as f:
            pass
        with open('test_app/apps.py', 'w') as f:
            f.write(TEST_APP)
        with open('test_app/models.py', 'w') as f:
            f.write(MODELS_FILE_CONTENT)
        with open('test_app/some_module.py', 'w') as f:
            f.write(SOME_MODULE_CONTENT)
        with open('test_app/main_navigation.py', 'w') as f:
            f.write(MAIN_NAVIGATION_CONTENT)
        with open('test_app/decorators.py', 'w') as f:
            f.write(DECORATORS_CONTENT)
        with open('test_app/context_processors.py', 'w') as f:
            f.write(CONTEXT_PROCESSOR_CONTENT)
        with open('test_app/urls.py', 'w') as f:
            f.write(TEST_APP_URLS)
        with open('test_app/views.py', 'w') as f:
            f.write(TEST_APP_VIEWS)

    # Load settings programmatically
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()

    call_command('migrate', verbosity=2)

# Register cleanup on exit to ensure proper file removal
def cleanup():
    if os.path.exists('templates'):
        shutil.rmtree('templates')
    if os.path.exists('test_app'):
        shutil.rmtree('test_app')
    if os.path.exists('test_project'):
        shutil.rmtree('test_project')


setup_django_project()
atexit.register(cleanup)


from django.test import TestCase, RequestFactory
from django.urls import reverse
from bs4 import BeautifulSoup

from test_app.context_processors import dynamic_admin_menu
from test_app.main_navigation import setup_navigation


class TestDynamicAdminMenu(TestCase):
    def setUp(self):
        # RequestFactory allows us to create mock requests for testing
        self.factory = RequestFactory()

    def test_admin_menu_view_renders_menu(self):
        """
        This test verifies that the `admin_menu_view` properly renders the 'menu.html' template
        with the correct navigation items. It uses Django's test client to request the view,
        and BeautifulSoup to parse and check the resulting HTML.
        """

        # Access the admin_menu_view via its URL
        response = self.client.get(reverse('admin-menu'))

        # Ensure the view returns a 200 HTTP status code
        self.assertEqual(response.status_code, 200)

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main menu list (assuming it's an <ul> with class "custom-admin-menu")
        menu = soup.find('ul')
        self.assertIsNotNone(menu, "The menu should be rendered as a <ul> element with class 'custom-admin-menu'.")

        # Verify that the main menu items are rendered
        main_items = menu.find_all('li', recursive=False)  # Only get the top-level <li> elements
        self.assertGreater(len(main_items), 0, "There should be main navigation items in the menu.")

        # Check that specific dynamically registered items are present
        expected_items = ['Dashboard', 'Hardware Management', 'Inventory Management', 'Administration']
        for item_text in expected_items:
            self.assertTrue(any(item_text in li.text for li in main_items), f"Main item '{item_text}' should be present.")

    def test_dynamic_admin_menu_in_context(self):
        """
        Test to verify that the 'dynamic_admin_menu' context processor
        adds 'menu_items' to the template context correctly.
        """
        # Simulate a GET request
        request = self.factory.get('/')

        # Call the context processor directly with the mock request
        context = dynamic_admin_menu(request)

        # Assert that 'menu_items' is present in the returned context
        self.assertIn('menu_items', context)

        # Verify that the menu items match the expected structure
        expected_navigation = setup_navigation()
        self.assertEqual(context['menu_items'], expected_navigation)

    def test_navigation_contains_all_registered_extensions(self):
        """
        Test to verify that registered extensions are correctly added
        to their respective menu clusters, based on their cluster_id.
        """
        # Simulate a GET request
        request = self.factory.get('/')

        # Get the context from the context processor
        context = dynamic_admin_menu(request)

        hardware_manager = next(item for item in context['menu_items'] if item['id'] == 'hardware_manager')
        hardware_manager_children_ids = [child['id'] for child in hardware_manager['children']]
        self.assertEqual(2, len(hardware_manager_children_ids))
        self.assertIn("circuit_boards", hardware_manager_children_ids)

        inventory_manager = next(item for item in context['menu_items'] if item['id'] == 'inventory_manager')
        inventory_manager_children_ids = [child['id'] for child in inventory_manager['children']]
        self.assertEqual(2, len(inventory_manager_children_ids))
        self.assertIn("product_frame_entries", inventory_manager_children_ids)


if __name__ == '__main__':
    unittest.main(verbosity=2)
