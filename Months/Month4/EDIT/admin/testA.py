import unittest
from ideal_completion import (
    register_navigation_item,
    setup_navigation,
    NAVIGATION_EXTENSIONS
)

class TestNavigationExtensions(unittest.TestCase):
    def setUp(self):
        # Clear any existing extensions before each test
        NAVIGATION_EXTENSIONS.clear()

    def test_add_item_to_hardware_manager(self):
        # Use the decorator to register a new item
        @register_navigation_item('hardware_manager', position=2)
        def hardware_manager_extensions():
            return [{
                'id': 'circuit_boards',
                'display_name': 'Boards',
                'model_name': 'Board',
                'icon': 'space_dashboard'
            }]

        # Generate the navigation structure
        navigation = setup_navigation()
        # Find the 'hardware_manager' cluster
        hardware_cluster = next(
            (item for item in navigation if item['id'] == 'hardware_manager'), None)
        self.assertIsNotNone(hardware_cluster)

        # Verify the new item is inserted at position 2
        expected_item = {
            'id': 'circuit_boards',
            'display_name': 'Boards',
            'model_name': 'Board',
            'icon': 'space_dashboard'
        }
        self.assertEqual(hardware_cluster['children'][2], expected_item)

    def test_add_item_to_inventory_manager(self):
        # Register a new item at the end of 'inventory_manager' cluster
        @register_navigation_item('inventory_manager', position='end')
        def inventory_manager_extensions():
            return [{
                'id': 'product_frame_entries',
                'display_name': 'Product frames',
                'model_name': 'ProductFrame',
                'icon': 'sd_card'
            }]

        navigation = setup_navigation()
        inventory_cluster = next(
            (item for item in navigation if item['id'] == 'inventory_manager'), None)
        self.assertIsNotNone(inventory_cluster)

        # Verify the new item is appended at the end
        expected_item = {
            'id': 'product_frame_entries',
            'display_name': 'Product frames',
            'model_name': 'ProductFrame',
            'icon': 'sd_card'
        }
        self.assertEqual(inventory_cluster['children'][-1], expected_item)

    def test_add_multiple_items_to_site_admin(self):
        # Register multiple items to 'site_admin' cluster
        @register_navigation_item('site_admin', position='end')
        def admin_extensions():
            return [
                {
                    'id': 'billing_log_for_projects',
                    'display_name': 'Project billing log',
                    'model_name': 'ProductFrameOperationLog',
                    'icon': 'receipt_long'
                },
                {
                    'id': 'rental_agreements',
                    'display_name': 'Leases',
                    'model_name': 'Lease',
                    'icon': 'handshake'
                }
            ]

        navigation = setup_navigation()
        admin_cluster = next(
            (item for item in navigation if item['id'] == 'site_admin'), None)
        self.assertIsNotNone(admin_cluster)

        # Verify the new items are appended at the end
        expected_items = [
            {
                'id': 'billing_log_for_projects',
                'display_name': 'Project billing log',
                'model_name': 'ProductFrameOperationLog',
                'icon': 'receipt_long'
            },
            {
                'id': 'rental_agreements',
                'display_name': 'Leases',
                'model_name': 'Lease',
                'icon': 'handshake'
            }
        ]
        self.assertEqual(admin_cluster['children'][-2:], expected_items)

if __name__ == '__main__':
    unittest.main()