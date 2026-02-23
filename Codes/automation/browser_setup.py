"""
Browser configuration and setup.
Anti-detection measures for web automation.
"""
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class BrowserSetup:
    """Handles browser configuration with anti-detection measures."""

    @staticmethod
    def setup_browser(headless=False):
        """
        Setup Edge browser with anti-detection measures.

        Args:
            headless (bool): Whether to run in headless mode.

        Returns:
            WebDriver: Configured Edge WebDriver instance.
        """
        options = webdriver.EdgeOptions()
        options.add_argument('--save-page-as-mhtml')
        options.add_argument('--enable-chrome-browser-cloud-management')

        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver.implicitly_wait(10)

        # Anti-detection: prevent navigator.webdriver detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

        return driver

    @staticmethod
    def setup_browser_for_fill():
        """
        Setup browser specifically for form filling (non-headless).

        Returns:
            WebDriver: Configured Edge WebDriver instance.
        """
        return BrowserSetup.setup_browser(headless=False)

    @staticmethod
    def setup_browser_for_analysis():
        """
        Setup browser for survey analysis (headless).

        Returns:
            WebDriver: Configured Edge WebDriver instance.
        """
        return BrowserSetup.setup_browser(headless=True)
