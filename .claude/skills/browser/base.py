"""
Base class for browser skills.
"""

from abc import abstractmethod
from typing import Dict, Any, List

from skills.base import BaseSkill, SkillCategory, SkillMetadata, SkillResult


class BrowserSkill(BaseSkill):
    """
    Base class for browser management skills.

    All browser skills should inherit from this class.
    Provides common functionality for browser operations.
    """

    # Common browser settings
    DEFAULT_USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )

    DEFAULT_VIEWPORT = {'width': 1920, 'height': 1080}
    DEFAULT_LOCALE = 'zh-CN'

    # Anti-detection script
    ANTI_DETECTION_SCRIPT = """
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
    """

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this browser skill."""
        pass

    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the browser task.

        Returns higher confidence for matching browser operations.
        """
        pass

    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute the browser operation.

        Args:
            task_data: Browser operation parameters

        Returns:
            SkillResult with success status and browser resources
        """
        pass

    def get_required_context_keys(self) -> List[str]:
        """Browser skills typically don't require existing context."""
        return []

    def _detect_channel(self) -> str | None:
        """
        Auto-detect available browser channel.

        Returns:
            "msedge", "chrome", or None for built-in Chromium
        """
        import platform
        import shutil
        import os

        system = platform.system()

        # Edge detection
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

        # Chrome detection
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

        return None

    def _ensure_playwright_browsers(self) -> None:
        """Install Playwright Chromium if not already present."""
        import subprocess

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

    def _apply_anti_detection(self, context) -> None:
        """Apply anti-detection scripts to browser context."""
        context.add_init_script(self.ANTI_DETECTION_SCRIPT)
