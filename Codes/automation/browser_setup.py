"""
Browser configuration and setup with Playwright.
Anti-detection measures for web automation.
"""
import os
import platform
import subprocess
import shutil
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserSetup:
    """Handles browser configuration with anti-detection measures using Playwright."""

    @staticmethod
    def _detect_channel():
        """Auto-detect available browser: prefer Edge, then Chrome, then built-in Chromium.

        Supports Windows, macOS, and Linux.
        """
        system = platform.system()

        # --- Edge detection ---
        if system == "Windows":
            edge_paths = [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            ]
            if shutil.which("msedge") or any(os.path.isfile(p) for p in edge_paths):
                return "msedge"
        elif system == "Darwin":
            mac_edge = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            if os.path.isfile(mac_edge) or shutil.which("msedge"):
                return "msedge"
        else:  # Linux
            if shutil.which("microsoft-edge-stable") or shutil.which("microsoft-edge") or shutil.which("msedge"):
                return "msedge"

        # --- Chrome detection ---
        if system == "Windows":
            chrome_paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            ]
            if shutil.which("chrome") or any(os.path.isfile(p) for p in chrome_paths):
                return "chrome"
        elif system == "Darwin":
            mac_chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.isfile(mac_chrome) or shutil.which("google-chrome"):
                return "chrome"
        else:  # Linux
            if shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium-browser") or shutil.which("chromium"):
                return "chrome"

        # Fall back to Playwright built-in Chromium (no channel)
        return None

    @staticmethod
    def _ensure_playwright_browsers():
        """Install Playwright Chromium if not already present."""
        try:
            subprocess.run(
                ["playwright", "install", "chromium"],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            # Also try via python -m
            subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                check=True,
                capture_output=True,
                text=True,
            )

    @staticmethod
    def setup_browser(headless=False, channel="auto"):
        """
        Setup browser with anti-detection measures using Playwright.

        Args:
            headless (bool): Whether to run in headless mode.
            channel: Browser channel to use.
                     "auto" - auto-detect (Edge -> Chrome -> built-in Chromium)
                     "msedge" / "chrome" - use the specified browser
                     None - use Playwright built-in Chromium

        Returns:
            tuple: (playwright_instance, browser, context, page) - Playwright instance, browser, context, and page.
        """
        if channel == "auto":
            channel = BrowserSetup._detect_channel()

        playwright_instance = sync_playwright().start()

        launch_kwargs = dict(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled'],
        )
        if channel is not None:
            launch_kwargs["channel"] = channel

        try:
            browser = playwright_instance.chromium.launch(**launch_kwargs)
        except Exception as e:
            if "Executable doesn't exist" in str(e) and channel is None:
                # Built-in Chromium not installed — download it automatically
                BrowserSetup._ensure_playwright_browsers()
                browser = playwright_instance.chromium.launch(**launch_kwargs)
            else:
                raise

        # Generic Chrome user-agent (no Edg/ suffix)
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        # Create context with anti-detection settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
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

        return playwright_instance, browser, context, page

    @staticmethod
    def setup_browser_for_fill(channel="auto"):
        """
        Setup browser specifically for form filling (non-headless).

        Args:
            channel: Browser channel to use (see setup_browser).

        Returns:
            tuple: (playwright_instance, browser, context, page) - Playwright instance, browser, context, and page.
        """
        return BrowserSetup.setup_browser(headless=False, channel=channel)

    @staticmethod
    def setup_browser_for_analysis():
        """
        Setup browser for survey analysis (headless).

        Returns:
            tuple: (playwright_instance, browser, context, page) - Playwright instance, browser, context, and page.
        """
        return BrowserSetup.setup_browser(headless=True)
