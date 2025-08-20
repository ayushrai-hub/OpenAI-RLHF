# context_processors.py
from django.urls import reverse

MENU_ITEMS = []

def register_menu_item(label, url):
    MENU_ITEMS.append({'label': label, 'url': url})

def custom_admin_menu(request):
    # Default menu items
    menu_items = [
        {'label': 'Dashboard', 'url': reverse('admin:index')},
        {'label': 'Projects', 'url': reverse('admin:app_list', kwargs={'app_label': 'projects'})},
    ]

    # Attach items from other apps
    menu_items.extend(MENU_ITEMS)
    
    return {'menu_items': menu_items}
