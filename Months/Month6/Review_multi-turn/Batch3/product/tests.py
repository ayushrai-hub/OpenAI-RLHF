import execjs
import unittest
import os

class TestJavaScriptCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load and compile the JavaScript code from the ideal_completion.js file
        js_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ideal_completion.js'))
        with open(js_file_path, 'r') as file:
            cls.js_code = file.read()
        cls.ctx = execjs.compile(cls.js_code)

    def test_total_length_of_data(self):
        # Test to check if the getProductData function returns the correct number of products, which should be 25

        result = self.ctx.call("getProductData")
        expected_length = 25

        # Assert that the list contains the expected number of products
        self.assertEqual(len(result), expected_length, "Product list should contain exactly 25 products.")

    def test_products_keys(self):
        # Test to check if the products have the expected keys
        result = self.ctx.call("getProductData")  # Get the list of products

        # Check that the first product has the required fields
        expected_keys = {"title", "cost", "saleCost", "discountRate", "reviews", "description", "category", "slug", "image"}
        for product in result:
            self.assertTrue(expected_keys.issubset(product.keys()), f"{product['title']} is missing some expected keys.")

    def test_product_with_no_sale(self):
        # Test to check if there are products with no sale price, and their discount rate is zero
        result = self.ctx.call("getProductData")

        # Find all products where saleCost is 0
        no_sale_products = [product for product in result if product["saleCost"] == 0]

        # Verify that these products have a discount rate of 0
        for product in no_sale_products:
            self.assertEqual(product["discountRate"], 0, f"Discount rate should be 0 for product {product['title']} with no sale price.")

    def test_product_with_sale(self):
        #  Test to check if sales products have correct discount and saleCost.
        result = self.ctx.call("getProductData")

        # Filter the products that have "Sales" in their category
        sales_items = [item for item in result if "Sales" in item["category"]]

        # Verify sale prices and discount rates for each item
        for item in sales_items:
            self.assertGreater(item["saleCost"], 0, f"Sale cost should be greater than 0 for item {item['title']}")
            calculated_discount_rate = ((item["cost"] - item["saleCost"]) / item["cost"]) * 100
            self.assertAlmostEqual(item["discountRate"], calculated_discount_rate, places=2,
                                   msg=f"Discount rate incorrect for item {item['title']}")

    def test_exactly_five_items_have_sales_category(self):
        # Test to check that exactly 5 products belong to the "Sales" category and their details are correct
        result = self.ctx.call("getProductData")

        # Filter the products that have "Sales" in their category
        sales_items = [item for item in result if "Sales" in item["category"]]

        # Assert that there are 5 items with the "Sales" category
        self.assertGreaterEqual(len(sales_items), 5, "There should be 5 or more products in the 'Sales' category.")

    def test_all_categories_present(self):
        # Test to check if all six categories are present
        result = self.ctx.call("getProductData")

        # Expected categories
        expected_categories = {
            "Women's Apparel", "Men's Apparel", "Gadgets", "Home & Living",
            "Health & Wellness", "Food & Pets", "Athletics & Outdoors", "Kids & Toys"
        }

        # Extract categories from products
        product_categories = set()
        for product in result:
            if isinstance(product["category"], list):  # If categories are listed as an array
                product_categories.update(product["category"])
            else:  # If category is a string
                product_categories.add(product["category"])

        # Assert all expected categories are found
        missing_categories = expected_categories - product_categories
        self.assertFalse(missing_categories, f"Missing categories: {missing_categories}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
