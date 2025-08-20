import unittest
import os
from playwright.sync_api import sync_playwright


def abs_path(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))


class TestDocumentScrolling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context(
            viewport={"width": 1280, "height": 720}, ignore_https_errors=True
        )

    def setUp(self):
        self.page = self.context.new_page()
        self.page.set_default_timeout(1000)
        self.page_path = abs_path("ideal_completion.html")
        self.page.goto(f"file://{self.page_path}")

    def tearDown(self):
        self.page.close()

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()

    def _is_element_visible(self, selector: str) -> bool:
        """Helper function to check if an element is visible in the viewport."""
        element = self.page.query_selector(selector)
        return element is not None and self.page.evaluate(
            "(element) => {"
            "  const rect = element.getBoundingClientRect();"
            "  return rect.top >= 0 && rect.bottom <= window.innerHeight && "
            "         rect.left >= 0 && rect.right <= window.innerWidth;"
            "}", 
            element
        )

    def test_skills_are_visible(self):
        try:
            # Scroll to the bottom of the page
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Confirm there's an h2 tag with text `Skills`
            skills_header = self.page.query_selector("h2:text('Skills')")
            self.assertIsNotNone(skills_header, "Skills header not found in viewport")

            # Confirm each skill list item is visible in the viewport using subTest for each skill
            skills = ["HTML", "CSS", "JavaScript", "Python", "Problem-solving"]
            for skill in skills:
                with self.subTest(skill=skill):
                    element = self.page.query_selector(f"li:text('{skill}')")
                    self.assertIsNotNone(element, f"{skill} not visible in viewport")
        except Exception as e:
            self.fail(str(e))


    def test_skills_visible_on_mobile(self):
        try:
            # Resize to mobile dimensions (412 x 915)
            self.page.set_viewport_size({"width": 412, "height": 915})

            # Scroll to #abilities
            self.page.evaluate("document.getElementById('abilities').scrollIntoView()")

            # Confirm there's an h2 tag with text `Skills`
            self.assertTrue(
                self._is_element_visible("h2:text('Skills')"),
                "Skills header not visible on mobile viewport"
            )

            # Confirm list items 'HTML', 'CSS', 'JavaScript', 'Python', and 'Problem-solving' are visible on mobile
            skills = ["HTML", "CSS", "JavaScript", "Python", "Problem-solving"]
            for skill in skills:
                with self.subTest(skill=skill):
                    selector = f"li:text('{skill}')"
                    self.assertTrue(
                        self._is_element_visible(selector),
                        f"{skill} not visible on mobile viewport"
                    )
        except Exception as e:
            self.fail(str(e))
            
    def test_projects_are_visible(self):
        try:
            # Scroll to the bottom of the page
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Confirm there's an h2 tag with text `Projects`
            projects_header = self.page.query_selector("h2:text('Projects')")
            self.assertIsNotNone(projects_header, "Projects header not found in viewport")

            # Confirm each project title is visible in the viewport using subTest for each project
            projects = ["First Website", "Calc App"]
            for project in projects:
                with self.subTest(project=project):
                    element = self.page.query_selector(f".project h3:text('{project}')")
                    self.assertIsNotNone(element, f"Project '{project}' not visible in viewport")
        except Exception as e:
            self.fail(str(e))

    def test_projects_visible_mobile(self):
        try:
            # Resize to mobile dimensions (412 x 915)
            self.page.set_viewport_size({"width": 412, "height": 915})
            self.page.evaluate("document.getElementById('work').scrollIntoView()")
            # Do not scroll manually here to test if they are truly within the viewport
            self.page.wait_for_timeout(500)  # Allow some time for rendering

            # Select all project divs
            project_divs = self.page.query_selector_all(".project")
            
            # Ensure at least some projects are found
            self.assertGreater(len(project_divs), 0, "No project elements found.")

            # Filter visible project divs based on bounding box within the viewport
            visible_projects = [
                div for div in project_divs if self.page.evaluate(
                    "(div) => {"
                    "  const rect = div.getBoundingClientRect();"
                    "  return rect.top >= 0 && rect.bottom <= window.innerHeight && "
                    "         rect.left >= 0 && rect.right <= window.innerWidth;"
                    "}", 
                    div
                )
            ]

            # Assert that exactly 2 project divs are visible
            self.assertEqual(
                len(visible_projects),
                2,
                f"Expected 2 visible project divs, found {len(visible_projects)}"
            )

            # Check that each visible project has the correct content
            expected_projects = ["First Website", "Calc App"]
            for expected in expected_projects:
                with self.subTest(project=expected):
                    self.assertTrue(
                        any(expected in div.inner_text() for div in visible_projects),
                        f"Project '{expected}' not visible in viewport"
                    )

        except Exception as e:
            self.fail(str(e))

    def test_footer_visible_on_scroll(self):
        try:
            # Ensure the viewport is mobile-sized but fits within screen limits
            self.page.set_viewport_size({"width": 400, "height": 900})

            # Scroll the footer into view
            self.page.evaluate("""
                document.querySelector('footer').scrollIntoView({ behavior: 'smooth', block: 'end' });
            """)
            self.page.wait_for_timeout(1000)  # Allow time for scrolling animation to finish

            #  # Confirm the footer is visible
            footer_visible = self._is_element_visible("footer")
            self.assertTrue(footer_visible, "Footer section not visible or fully within viewport")

        except Exception as e:
            self.fail(f"Test failed due to: {str(e)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
