"""
Browser configuration and setup with Playwright.
Anti-detection measures for web automation.
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserSetup:
    """Handles browser configuration with anti-detection measures using Playwright."""

    @staticmethod
    def setup_browser(headless=False):
        """
        Setup Edge browser with anti-detection measures using Playwright.

        Args:
            headless (bool): Whether to run in headless mode.

        Returns:
            tuple: (browser, context, page) - Playwright browser instance, context, and page.
        """
        playwright_instance = sync_playwright().start()

        browser = playwright_instance.chromium.launch(
            channel="msedge",
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Create context with anti-detection settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            locale='zh-CN'
        )

        # Anti-detection scripts
        context.add_init_script("""
            // Hide webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Hide automation indicator
            window.chrome = {
                runtime: {}
            };

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });
        """)

        page = context.new_page()
        page.set_default_timeout(10000)
        page.set_default_navigation_timeout(30000)

        return browser, context, page

    @staticmethod
    def setup_browser_for_fill():
        """
        Setup browser specifically for form filling (non-headless).

        Returns:
            tuple: (browser, context, page) - Playwright browser instance, context, and page.
        """
        return BrowserSetup.setup_browser(headless=False)

    @staticmethod
    def setup_browser_for_analysis():
        """
        Setup browser for survey analysis (headless).

        Returns:
            tuple: (browser, context, page) - Playwright browser instance, context, and page.
        """
        return BrowserSetup.setup_browser(headless=True)
