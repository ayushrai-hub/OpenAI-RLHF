import unittest
from bs4 import BeautifulSoup
import os

class TestIdealCompletionHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the HTML content from the file
        with open(os.path.join(os.path.dirname(__file__), 'ideal_completion.html'), 'r') as f:
            cls.soup = BeautifulSoup(f, 'html.parser')

    def test_title(self):
        # Test if the page title is correct
        title = self.soup.title.string
        self.assertEqual(title, 'Product Store', 'Page title does not match expected value.')

    def test_header_elements(self):
        # Test if the header contains the logo and navigation items
        header = self.soup.find('header')
        self.assertIsNotNone(header, 'Header not found.')
        logo = header.find('div', class_='logo')
        self.assertIsNotNone(logo, 'Logo not found in header.')
        nav_items = header.find_all('a')
        expected_nav = {'Home', 'Products', 'Contact'}
        found_nav = {item.text for item in nav_items}
        self.assertEqual(found_nav, expected_nav, 'Navigation items do not match expected values.')

    def test_products_section(self):
        # Test if the products section exists and contains products
        products_section = self.soup.find('section', id='products')
        self.assertIsNotNone(products_section, 'Products section not found.')
        product_list = products_section.find('div', class_='product-list')
        self.assertIsNotNone(product_list, 'Product list not found in products section.')
        products = product_list.find_all('div', class_='product')
        self.assertGreater(len(products), 0, 'No products found in product list.')

    def test_chatbot_widget(self):
        # Test if the chatbot widget and toggle button are present
        chatbot = self.soup.find('div', id='chatbot')
        self.assertIsNotNone(chatbot, 'Chatbot widget not found.')
        toggle_button = chatbot.find('button', id='chatbot-toggle')
        self.assertIsNotNone(toggle_button, 'Chatbot toggle button not found.')
        chatbox = chatbot.find('div', id='chatbox')
        self.assertIsNotNone(chatbox, 'Chatbox not found inside chatbot widget.')

if __name__ == '__main__':
    unittest.main(verbosity=2)
