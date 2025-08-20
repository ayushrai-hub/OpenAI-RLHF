import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from urllib.parse import quote
from selenium.webdriver.common.by import By
import os

class TestCatalogFiltering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Selenium with ChromeDriver
        cls.chrome_options = Options()
        cls.chrome_options.add_argument("--headless")  # Run in headless mode
        cls.chrome_options.add_argument("--no-sandbox")  # MUST HAVE THIS
        cls.chrome_options.add_argument("--disable-dev-shm-usage")  # MUST HAVE THIS
        cls.driver = webdriver.Chrome(service=ChromeService(), options=cls.chrome_options)
        
        # Load the HTML content from the file
        with open(os.path.join(os.path.dirname(__file__), "ideal_completion.html"), 'r', encoding='utf-8') as f:
            html_content = f.read()

        encoded_html = 'data:text/html;charset=utf-8,' + quote(html_content)
        cls.driver.get(encoded_html)
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def setUp(self):
        # Refresh the page to reset state before each test
        self.driver.refresh()
    
    def test_initial_state(self):
        # Check the visibility of both the webtoon and comic section
        webtoon_section = self.driver.find_element(By.CSS_SELECTOR,"#webtoon")
        comic_section = self.driver.find_element(By.CSS_SELECTOR,"#comic")
        self.assertEqual(webtoon_section.is_displayed(),comic_section.is_displayed())

    def test_every_webtoon_displays_all_webtoons(self):
        self.driver.find_element('xpath', "//button[text()='READ']").click()
        self.driver.find_element('link text', 'WEBTOON').click()
        # Create sample entries
        self.create_webtoon_entry('Webtoon A', '10', 'Currently Viewing')
        self.create_webtoon_entry('Webtoon B', '5', 'Finished')
        self.create_webtoon_entry('Webtoon C', '20', 'Paused')
        
        # Click on category 'Every Webtoon'
        self.driver.find_element('xpath', "//section[@id='webtoon']//a[text()='Every Webtoon']").click()
        
        # Verify the category title
        category_title = self.driver.find_element('xpath', "//section[@id='webtoon']//h1[@id='category']").text
        self.assertEqual(category_title, 'EVERY WEBTOON')
        
        # Verify all entries are displayed
        entries = self.driver.find_elements('xpath', "//section[@id='webtoon']//div[@class='entries']//div[@class='entry-item']")
        displayed_entries = [entry for entry in entries if entry.is_displayed()]
        self.assertEqual(len(displayed_entries), 3)

    def test_finished_webtoons_displays_only_finished(self):

        self.driver.find_element('xpath', "//button[text()='READ']").click()
        self.driver.find_element('link text', 'WEBTOON').click()
        # Create sample entries
        self.create_webtoon_entry('Webtoon A', '10', 'Currently Viewing')
        self.create_webtoon_entry('Webtoon B', '5', 'Finished')
        self.create_webtoon_entry('Webtoon C', '20', 'Finished')
        
        # Click on category 'Finished'
        self.driver.find_element('xpath', "//section[@id='webtoon']//a[text()='Finished']").click()
        
        # Verify the category title
        category_title = self.driver.find_element('xpath', "//section[@id='webtoon']//h1[@id='category']").text
        self.assertEqual(category_title, 'FINISHED')
        
        # Verify only 'Finished' entries are displayed
        entries = self.driver.find_elements('xpath', "//section[@id='webtoon']//div[@class='entries']//div[@class='entry-item']")
        displayed_entries = [entry for entry in entries if entry.is_displayed()]
        self.assertEqual(len(displayed_entries), 2)
        for entry in displayed_entries:
            data_group = entry.get_attribute('data-group')
            self.assertEqual(data_group, 'Finished')

    def test_every_comic_displays_all_comics(self):

        # Go to the 'COMIC' section
        self.driver.find_element('xpath', "//button[text()='READ']").click()
        self.driver.find_element('link text', 'COMIC').click()
        
        # Create sample entries
        self.create_comic_entry('Comic A', '15', 'Currently Viewing')
        self.create_comic_entry('Comic B', '7', 'Finished')
        self.create_comic_entry('Comic C', '12', 'Paused')
        
        # Click on category 'Every Comic'
        self.driver.find_element('xpath', "//section[@id='comic']//a[text()='Every Comic']").click()
        
        # Verify the category title
        category_title = self.driver.find_element('xpath', "//section[@id='comic']//h1[@id='category']").text
        self.assertEqual(category_title, 'EVERY COMIC')
        
        # Verify all entries are displayed
        entries = self.driver.find_elements('xpath', "//section[@id='comic']//div[@class='entries']//div[@class='entry-item']")
        displayed_entries = [entry for entry in entries if entry.is_displayed()]
        self.assertEqual(len(displayed_entries), 3)

    def test_finished_comics_displays_only_finished(self):
        self.driver.find_element('xpath', "//button[text()='READ']").click()
        self.driver.find_element('link text', 'COMIC').click()
        # Create sample entries for comics
        self.create_comic_entry('Comic D', '8', 'Currently Viewing')
        self.create_comic_entry('Comic E', '22', 'Finished')
        self.create_comic_entry('Comic F', '15', 'Finished')
        
        # Click on the category 'Finished' in the Comic section
        self.driver.find_element('xpath', "//section[@id='comic']//a[text()='Finished']").click()
        
        # Verify the category title is correct
        category_title = self.driver.find_element('xpath', "//section[@id='comic']//h1[@id='category']").text
        self.assertEqual(category_title, 'FINISHED')
        
        # Verify only 'Finished' entries are displayed
        entries = self.driver.find_elements('xpath', "//section[@id='comic']//div[@class='entries']//div[@class='entry-item']")
        displayed_entries = [entry for entry in entries if entry.is_displayed()]
        self.assertEqual(len(displayed_entries), 2)  # Expecting only two entries to be displayed
        for entry in displayed_entries:
            data_group = entry.get_attribute('data-group')
            self.assertEqual(data_group, 'Finished')
    
    def create_webtoon_entry(self, title, chapter_count, group):
        # Fill in the form to create a webtoon entry
        name_input = self.driver.find_element('xpath', "//section[@id='webtoon']//input[@type='text']")
        name_input.clear()
        name_input.send_keys(title)
        
        count_input = self.driver.find_element('xpath', "//section[@id='webtoon']//input[@type='number']")
        count_input.clear()
        count_input.send_keys(chapter_count)
        
        group_select = self.driver.find_element('xpath', "//section[@id='webtoon']//select[@name='group']")
        group_select.find_element('xpath', f".//option[text()='{group}']").click()
        
        create_button = self.driver.find_element('xpath', "//section[@id='webtoon']//a[@class='createButton']")
        create_button.click()
    
    def create_comic_entry(self, title, chapter_count, group):
        # Fill in the form to create a comic entry
        name_input = self.driver.find_element('xpath', "//section[@id='comic']//input[@type='text']")
        name_input.clear()
        name_input.send_keys(title)
        
        count_input = self.driver.find_element('xpath', "//section[@id='comic']//input[@type='number']")
        count_input.clear()
        count_input.send_keys(chapter_count)
        
        group_select = self.driver.find_element('xpath', "//section[@id='comic']//select[@name='group']")
        group_select.find_element('xpath', f".//option[text()='{group}']").click()
        
        create_button = self.driver.find_element('xpath', "//section[@id='comic']//a[@class='createButton']")
        create_button.click()


if __name__ == '__main__':
    unittest.main(verbosity=2)