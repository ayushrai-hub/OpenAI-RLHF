# ideal_completion.py

SOME_MODULE_CONTENT = '''
from test_app.decorators import register_navigation_item

@register_navigation_item('hardware_manager', position=2)
def hardware_manager_extensions():
    return [{'id': 'circuit_boards', 'display_name': 'Boards', 'model_name': 'Board', 'icon': 'space_dashboard'}]

@register_navigation_item('inventory_manager', position='end')
def inventory_manager_extensions():
    return [{'id': 'product_frame_entries', 'display_name': 'Product frames', 'model_name': 'ProductFrame', 'icon': 'sd_card'}]
'''


from test_app.decorators import NAVIGATION_EXTENSIONS

def setup_navigation():
    NAVIGATION = [
        {'id': 'dashboard_main', 'display_name': 'Dashboard', 'url': '/'},
        {'id': 'license_manager', 'display_name': 'License Management', 'children': [
            {'id': 'all_licenses_overview', 'display_name': 'All licenses', 'model_name': 'BaseLicense', 'icon': 'all_inbox'}
        ]},
        {'id': 'hardware_manager', 'display_name': 'Hardware Management', 'children': [
            {'id': 'hardware_overview', 'display_name': 'All hardware units', 'model_name': 'BaseHardware', 'icon': 'all_inbox'}
        ]},
        {'id': 'inventory_manager', 'display_name': 'Inventory Management', 'children': [
            {'id': 'items_overview', 'display_name': 'Inventory items', 'model_name': 'InventoryElement', 'icon': 'inventory_2'}
        ]},
        {'id': 'site_admin', 'display_name': 'Administration', 'children': [
            {'id': 'user_accounts', 'display_name': 'Users', 'model_name': 'User', 'icon': 'person'}
        ]}
    ]

    # Add extensions from other modules
    for cluster in NAVIGATION:
        cluster_id = cluster['id']
        if cluster_id in NAVIGATION_EXTENSIONS:
            for func, position in NAVIGATION_EXTENSIONS[cluster_id]:
                additional_items = func()
                if position == 'start':
                    cluster['children'] = additional_items + cluster['children']
                elif position == 'end' or position is None:
                    cluster['children'].extend(additional_items)
                else:
                    cluster['children'][position:position] = additional_items

    return NAVIGATION



NAVIGATION_EXTENSIONS = {}

def register_navigation_item(cluster_id, position=None):
    """
    Decorator to register additional menu items to specific clusters.
    :param cluster_id: The ID of the cluster to which this item should be added.
    :param position: Specify the position to insert the item ('start', 'end', or specific index).
    """
    def decorator(func):
        # Ensure the cluster exists in the extensions
        if cluster_id not in NAVIGATION_EXTENSIONS:
            NAVIGATION_EXTENSIONS[cluster_id] = []

        # Add function to list of extensions for this cluster
        NAVIGATION_EXTENSIONS[cluster_id].append((func, position))
        return func
    return decorator


CONTEXT_PROCESSOR_CONTENT = '''
from test_app.main_navigation import setup_navigation

def dynamic_admin_menu(request):
    menu_items = setup_navigation()
    return {'menu_items': menu_items}
'''

MENU_TEMPLATE_CONTENT = '''
<ul>
{% for item in menu_items %}
    <li>
        {{ item.display_name }}
        {% if item.children %}
            <ul>
                {% for child in item.children %}
                    <li>{{ child.display_name }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    </li>
{% endfor %}
</ul>
'''

TEMPLATES_CONTENT = '''
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'test_app.context_processors.dynamic_admin_menu',
            ],
        },
    },
]
'''