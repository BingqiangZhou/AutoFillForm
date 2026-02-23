"""
URL change detection for form submission verification.
Custom Selenium wait condition.
"""


class url_has_changed:
    """Custom wait condition to check if URL has changed."""

    def __init__(self, old_url):
        self.old_url = old_url

    def __call__(self, driver):
        """Returns True if the current URL is different from the old URL."""
        return driver.current_url != self.old_url
