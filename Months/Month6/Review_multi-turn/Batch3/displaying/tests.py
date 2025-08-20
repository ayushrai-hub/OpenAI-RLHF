from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
from bs4 import BeautifulSoup
import base64
import os

class TestConsignmentDetails(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Load the HTML content from ideal_completion.html
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ideal_completion.html')), 'r', encoding='utf-8') as f:
            self.html_content = f.read()

        # Encode HTML content to base64
        self.encoded_html = base64.b64encode(self.html_content.encode('utf-8')).decode('utf-8')

        # Set up Selenium with ChromeDriver
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")  # MUST HAVE THIS
        self.chrome_options.add_argument("--disable-dev-shm-usage")  # MUST HAVE THIS
        self.driver = webdriver.Chrome(service=ChromeService(), options=self.chrome_options)
    
    @classmethod
    def tearDown(self):
        self.driver.refresh()

    def setUp(self):
        # Load the HTML content into the browser before each test
        self.driver.get("data:text/html;charset=utf-8;base64," + self.encoded_html)

    def enter_value(self):
        # Wait for the serialNoInput field to be visible
        serial_no_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "serialNoInput"))
        )
        serial_no_input.clear()
        serial_no_input.send_keys("12345")

    def mock_fetch_with_new_data(self, mock_data):
        # Convert mock data to a JavaScript object
        mock_data_js = str(mock_data).replace("'", '"')  # Ensure valid JSON format
        # Inject JavaScript to mock fetch
        self.driver.execute_script(f"""
            const originalFetch = window.fetch;
            window.fetch = function(input, init) {{
                // Mock response for specific URL or all fetch requests
                if (typeof input === 'string' && input.includes('FetchDataServlet')) {{
                    return Promise.resolve(new Response(JSON.stringify({mock_data_js}), {{
                        status: 200,
                        headers: {{
                            'Content-Type': 'application/json'
                        }}
                    }}));
                }}
                return originalFetch(input, init);
            }};
        """)

    def bypass_window_onload(self):
        self.driver.execute_script("""
            // Override window.onload to bypass the emp_name check
            window.onload = function() {
                console.log('Bypassing emp_name check');
                retrieveAndDisplayTable(); // Directly call the table retrieval function
            };
        """)

    def test_data_population(self):
        mock_data = {
            "loadingDataArray": [
                {"serialKey": "REF/2025 - 1111111111",
                "empName": "<ANOTHER_EMAIL>",
                "empNo": "67890", 
                "vehicleNo": "7654321",
                "transportName": "Transporter Three",
                "dealerEmail": "Dealer Contact 5", 
                "location": "Whitefield, Bangalore East, Karnataka, India, 560066",
                "totalBoxWeight": "50/221.50kg", 
                "createdTime": "2025-10-12 08:45:22"}, 
            ],
            "scanMasterDataArray": [
                {"serialKey": "REF/2025 - 1111111111", "SerialNo": "654321", "Weight": 3.56}, 
                {"serialKey": "REF/2025 - 1111111111", "SerialNo": "654321", "Weight": 3.56}
            ]
        }
        self.bypass_window_onload()
        # Inject mock fetch
        self.mock_fetch_with_new_data(mock_data)
        self.enter_value()
        self.driver.find_element(By.ID, "filterButton").click()
        self.driver.implicitly_wait(5)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        rows = soup.select('#dataTable tbody tr')  # Select all rows in the table body
        # Check the contents of the first row
        first_row_cells = rows[0].find_all('td')
        self.assertEqual(first_row_cells[0].text.strip(), '1')  # ID
        self.assertEqual(first_row_cells[1].text.strip(), '2025-10-12 08:45:22')  # Created Time
        self.assertEqual(first_row_cells[2].text.strip(), '7654321')  # Vehicle No
        self.assertEqual(first_row_cells[3].text.strip(), 'Transporter Three')  # Transport Name
        self.assertEqual(first_row_cells[4].text.strip(), 'Dealer Contact 5')  # Dealer Email
        self.assertEqual(first_row_cells[5].text.strip(), 'Whitefield, Bangalore East, Karnataka, India, 560066')  # Location
        self.assertEqual(first_row_cells[6].text.strip(), '654321')  # Serial No
        self.assertEqual(first_row_cells[7].text.strip(), '3.56 kg')  # Weight

        
    def test_no_data_available(self):
        # Test that 'No data available' message is shown when no data is returned
        self.bypass_window_onload()
        self.enter_value()
        self.driver.find_element(By.ID, "filterButton").click()
        self.driver.implicitly_wait(5)
        self.driver.execute_script("""
            // Clear the table body
            let tableBody = document.querySelector('#dataTable tbody');
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No data found for the selected serial number.</td></tr>';
            }

            // Clear inputs or other fields if necessary
            document.getElementById('totalBoxWeight').value = '';
        """)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        no_data_message = soup.find_all(string="No data found for the selected serial number.")
        self.assertTrue(no_data_message, "No data available message should be visible.")

    def test_total_weight_calculation(self):
        # Test that totalBoxWeight input shows correct calculation
        mock_data = {
            "loadingDataArray": [
                {"serialKey": "REF/2025 - 1111111111",
                "empName": "<ANOTHER_EMAIL>",
                "empNo": "67890", 
                "vehicleNo": "7654321",
                "transportName": "Transporter Three",
                "dealerEmail": "Dealer Contact 5", 
                "location": "Whitefield, Bangalore East, Karnataka, India, 560066",
                "totalBoxWeight": "50/221.50kg", 
                "createdTime": "2025-10-12 08:45:22"}, 
            ],
            "scanMasterDataArray": [
                {"serialKey": "REF/2025 - 1111111111", "SerialNo": "654321", "Weight": 3.56}, 
                {"serialKey": "REF/2025 - 1111111111", "SerialNo": "654321", "Weight": 3.56}
            ]
        }

        # Inject mock fetch
        self.bypass_window_onload()
        self.mock_fetch_with_new_data(mock_data)
        self.enter_value()
        self.driver.find_element(By.ID, "filterButton").click()
        self.driver.implicitly_wait(5)

        total_weight_input = self.driver.find_element(By.ID, "totalBoxWeight").get_attribute('value')
        expected_value = "2 box / 7.12 kg"  # Expected value
        self.assertEqual(total_weight_input.strip(), expected_value.strip(), "Total weight should be calculated correctly.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
