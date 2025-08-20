import unittest
import os
from bs4 import BeautifulSoup

class TestTrendAnalyzerHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the HTML content from the file
        file_path = os.path.join(os.path.dirname(__file__), 'ideal_completion.html')
        with open(file_path, 'r') as f:
            cls.soup = BeautifulSoup(f, 'html.parser')

    def test_title(self):
        # Test if the title is correct
        title = self.soup.title.string
        self.assertEqual(title, 'Mutual Fund Trend Analyzer')

    def test_search_input_exists(self):
        # Test if the search input exists with id 'search'
        search_input = self.soup.find('input', {'id': 'search'})
        self.assertIsNotNone(search_input)

    def test_fund_checkboxes_div_exists(self):
        # Test if the div with id 'fund-checkboxes' exists
        fund_checkboxes_div = self.soup.find('div', {'id': 'fund-checkboxes'})
        self.assertIsNotNone(fund_checkboxes_div)

    def test_selected_funds_table_exists(self):
        # Test if the table with id 'fund-details' exists
        fund_details_table = self.soup.find('table', {'id': 'fund-details'})
        self.assertIsNotNone(fund_details_table)

    def test_canvas_exists_for_graph(self):
        # Test if the canvas element for the graph exists
        canvas = self.soup.find('canvas', {'id': 'trend-graph'})
        self.assertIsNotNone(canvas)

    def test_date_selectors_exist(self):
        # Test if date selector inputs exist
        start_date = self.soup.find('input', {'id': 'start-date'})
        end_date = self.soup.find('input', {'id': 'end-date'})
        self.assertIsNotNone(start_date)
        self.assertIsNotNone(end_date)

    def test_required_table_columns(self):
        # Test if all required columns are present in the table
        headers = self.soup.find('table', {'id': 'fund-details'}).find_all('th')
        required_columns = [
            'Scheme Name', 'Scheme Category', 'Current Date', 'Current NAV',
            '5-Year CAGR (%)', '3-Year CAGR (%)', 'YTD Change (%)', '1-Month Change (%)'
        ]
        header_text = [h.text.strip() for h in headers]
        for column in required_columns:
            self.assertIn(column, header_text)

    def test_search_input_placeholder(self):
        # Test if search input has appropriate placeholder
        search_input = self.soup.find('input', {'id': 'search'})
        self.assertIsNotNone(search_input.get('placeholder'))
        self.assertTrue('search' in search_input.get('placeholder').lower())

    def test_responsive_design_elements(self):
        # Test if responsive design elements are present
        canvas = self.soup.find('canvas', {'id': 'trend-graph'})
        self.assertTrue('max-width' in canvas.get('style', '') or 
                       any('max-width' in style.text for style in self.soup.find_all('style')))

    def test_date_selector_default_values(self):
        # Test if the date selectors have default values
        start_date = self.soup.find('input', {'id': 'start-date'})
        end_date = self.soup.find('input', {'id': 'end-date'})
        self.assertEqual(start_date.get('type'), 'date')
        self.assertEqual(end_date.get('type'), 'date')

    def test_fund_table_header_styling(self):
        # Test if the headers are bold
        headers = self.soup.find('table', {'id': 'fund-details'}).find('th')
        header_style = headers.get('style', '') + self.soup.find('style').text
        self.assertTrue('bold' in header_style.lower())

    def test_checkbox_exists_in_fund_list(self):
        # Test if the checkbox exists in the fund list
        fund_checkboxes = self.soup.find('div', {'id': 'fund-checkboxes'})
        checkbox_input = fund_checkboxes.find('input', {'type': 'checkbox'})
        self.assertIsNotNone(checkbox_input)

    def test_graph_styling(self):
        # Test if the graph is plotted as needed and the page is aesthetically very attractive
        canvas = self.soup.find('canvas', {'id': 'trend-graph'})
        canvas_style = canvas.get('style', '') + self.soup.find('style').text
        self.assertTrue('height' in canvas_style.lower())
        self.assertTrue('margin' in canvas_style.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
