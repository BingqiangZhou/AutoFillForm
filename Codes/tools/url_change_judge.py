"""
URL change detection for form submission verification.
Migrated from Selenium to Playwright.
"""


class url_has_changed:
    """Helper class to check if URL has changed using Playwright."""

    def __init__(self, old_url):
        self.old_url = old_url

    def __call__(self, page):
        """
        Returns True if the current URL is different from the old URL.

        Args:
            page: Playwright Page instance.

        Returns:
            bool: True if URL has changed.
        """
        return page.url != self.old_url


def wait_for_url_change(page, old_url, timeout=10000):
    """
    Wait for the URL to change using Playwright's wait_for_function.

    Args:
        page: Playwright Page instance.
        old_url (str): The original URL to compare against.
        timeout (int): Maximum time to wait in milliseconds.

    Returns:
        bool: True if URL changed, False if timeout.
    """
    try:
        page.wait_for_function(
            "url => window.location.href !== url",
            arg=old_url,
            timeout=timeout
        )
        return True
    except Exception:
        return False
