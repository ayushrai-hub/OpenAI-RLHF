import unittest
import os
from playwright.sync_api import sync_playwright


class TestHTMLContent(unittest.TestCase):
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()

        with open(
            os.path.join(os.path.dirname(__file__), "ideal_completion.html")
        ) as f:
            html_content = f.read()

        self.page.set_content(html_content)

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()

    def create_and_verify_webtoon_item(self, title, chapter, group):
        webtoon_title_input_field = self.page.locator(
            "#webtoon input[placeholder='Webtoon Title']"
        )
        webtoon_title_input_field.fill(title)

        webtoon_chapter_input_field = self.page.locator(
            "#webtoon input[placeholder='Chapter Count']"
        )
        webtoon_chapter_input_field.fill(chapter)

        select_element = self.page.locator("#webtoon select[name='group']")
        select_element.select_option(group)

        create_button = self.page.locator("#webtoon .createButton")
        create_button.click()

        link_element = self.page.locator(f"#webtoon a:text-is('{group}')")
        link_element.click()
        webtoon_currently_viewing_item = self.page.locator(
            f"#webtoon div.entry-item[data-group='{group}'] div.entry-item-content span.entry-title"
        )
        webtoon_currently_viewing_item_text = (
            webtoon_currently_viewing_item.text_content()
        )
        self.assertEqual(webtoon_currently_viewing_item_text, title)

    def create_and_verify_comic_item(self, title, chapter, group):
        comic_title_input_field = self.page.locator(
            "#comic input[placeholder='Comic Title']"
        )
        comic_title_input_field.fill(title)

        comic_chapter_input_field = self.page.locator(
            "#comic input[placeholder='Chapter Count']"
        )
        comic_chapter_input_field.fill(chapter)

        select_element = self.page.locator("#comic select[name='group']")
        select_element.select_option(group)

        create_button = self.page.locator("#comic .createButton")
        create_button.click()

        link_element = self.page.locator(f"#comic a:text-is('{group}')")
        link_element.click()
        comic_currently_viewing_item = self.page.locator(
            f"#comic div.entry-item[data-group='{group}'] div.entry-item-content span.entry-title"
        )
        comic_currently_viewing_item_text = comic_currently_viewing_item.text_content()
        self.assertEqual(comic_currently_viewing_item_text, title)

    def test_initial_state(self):
        webtoon_is_visible = self.page.locator("#webtoon").is_visible()
        comic_is_visible = self.page.locator("#comic").is_visible()
        is_both_visible = webtoon_is_visible and comic_is_visible
        self.assertEqual(
            is_both_visible,
            False,
            "Both Webtoon and Comic tab should not be visible at the same time",
        )

    def test_switch_between_webtoon_and_comic(self):
        webtoon_link = self.page.locator("a:text-is('WEBTOON')")
        webtoon_link.click()
        webtoon_is_visible = self.page.locator("#webtoon").is_visible()
        self.assertEqual(webtoon_is_visible, True, "Webtoon should be visible")

        comic_link = self.page.locator("a:text-is('COMIC')")
        comic_link.click()
        comic_is_visible = self.page.locator("#comic").is_visible()
        self.assertEqual(comic_is_visible, True, "Comic should be visible")

    def test_filter_webtoon(self):
        webtoon_link = self.page.locator("a:text-is('WEBTOON')")
        webtoon_link.click()
        self.create_and_verify_webtoon_item(
            "Current Viewing Webtoon", "1", "Currently Viewing"
        )
        self.create_and_verify_webtoon_item("Finished Webtoon", "1", "Finished")
        self.create_and_verify_webtoon_item("Paused Webtoon", "1", "Paused")
        self.create_and_verify_webtoon_item("Discontinued Webtoon", "1", "Discontinued")
        self.create_and_verify_webtoon_item("To Read Webtoon", "1", "To Read")

        every_webtoon_link_element = self.page.locator(
            f"#webtoon a:text-is('Every Webtoon')"
        )
        every_webtoon_link_element.click()
        webtoon_entries_element = self.page.locator("#webtoon div.entries")

        children = webtoon_entries_element.locator(":scope > *")
        for i in range(children.count()):
            is_visible = children.nth(i).is_visible()
            self.assertEqual(is_visible, True, f"Webtoon child {i + 1} is not visible.")

    def test_filter_comic(self):
        comic_link = self.page.locator("a:text-is('COMIC')")
        comic_link.click()
        self.create_and_verify_comic_item(
            "Current Viewing Comic", "1", "Currently Viewing"
        )
        self.create_and_verify_comic_item("Finished Comic", "1", "Finished")
        self.create_and_verify_comic_item("Paused Comic", "1", "Paused")
        self.create_and_verify_comic_item("Discontinued Comic", "1", "Discontinued")
        self.create_and_verify_comic_item("To Read Comic", "1", "To Read")

        every_comic_link_element = self.page.locator(f"#comic a:text-is('Every Comic')")
        every_comic_link_element.click()
        comic_entries_element = self.page.locator("#comic div.entries")

        children = comic_entries_element.locator(":scope > *")
        for i in range(children.count()):
            is_visible = children.nth(i).is_visible()
            self.assertEqual(is_visible, True, f"Comic child {i + 1} is not visible.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
