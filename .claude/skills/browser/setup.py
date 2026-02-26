"""
Browser setup skill for initializing browser instances.
"""

from typing import Dict, Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.browser.base import BrowserSkill
from skills.context import SkillContext


class BrowserSetupSkill(BrowserSkill):
    """
    Skill for setting up browser instances with anti-detection measures.

    Supports headless and non-headless modes, with automatic browser detection.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="browser_setup",
            display_name="浏览器启动",
            description="启动浏览器实例，支持无头/有头模式，自动检测可用浏览器",
            category=SkillCategory.BROWSER,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.CRITICAL,
            tags=["browser", "setup", "init", "浏览器", "启动"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_type is 'browser_setup' or similar
        - task_data contains 'headless' key
        """
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["browser_setup", "setup_browser", "init_browser", "浏览器启动"]:
            return 1.0

        if "headless" in task_data:
            return 0.8

        if "channel" in task_data:
            return 0.7

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute browser setup.

        Args:
            task_data: Must contain:
                - headless: bool - Whether to run in headless mode
                - channel: str - Browser channel ("auto", "msedge", "chrome", None)

        Returns:
            SkillResult with browser resources
        """
        try:
            headless = task_data.get("headless", False)
            channel = task_data.get("channel", "auto")

            if channel == "auto":
                channel = self._detect_channel()

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
                    self._ensure_playwright_browsers()
                    browser = playwright_instance.chromium.launch(**launch_kwargs)
                else:
                    raise

            # Create context with anti-detection settings
            context = browser.new_context(
                viewport=self.DEFAULT_VIEWPORT,
                user_agent=self.DEFAULT_USER_AGENT,
                locale=self.DEFAULT_LOCALE
            )

            # Apply anti-detection scripts
            self._apply_anti_detection(context)

            # Create page
            page = context.new_page()
            page.set_default_timeout(10000)
            page.set_default_navigation_timeout(30000)

            return SkillResult.success_result(
                data={
                    "playwright_instance": playwright_instance,
                    "browser": browser,
                    "context": context,
                    "page": page,
                },
                metadata={
                    "headless": headless,
                    "channel": channel,
                    "user_agent": self.DEFAULT_USER_AGENT,
                    "viewport": self.DEFAULT_VIEWPORT,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Browser setup failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate browser setup input."""
        headless = task_data.get("headless")
        if headless is not None and not isinstance(headless, bool):
            return False

        channel = task_data.get("channel")
        if channel is not None and channel not in ["auto", "msedge", "chrome", None]:
            return False

        return True


class BrowserSetupForFillSkill(BrowserSetupSkill):
    """
    Skill for setting up browser specifically for form filling (non-headless).
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="browser_setup_for_fill",
            display_name="浏览器启动(填写模式)",
            description="启动有头浏览器用于表单填写",
            category=SkillCategory.BROWSER,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["browser", "fill", "填写"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """Check if this is for form filling."""
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["browser_setup_for_fill", "fill_browser", "填写浏览器"]:
            return 1.0
        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """Execute browser setup for form filling."""
        task_data = {**task_data, "headless": False}
        return super().execute(task_data)


class BrowserSetupForAnalysisSkill(BrowserSetupSkill):
    """
    Skill for setting up browser for survey analysis (headless).
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="browser_setup_for_analysis",
            display_name="浏览器启动(分析模式)",
            description="启动无头浏览器用于问卷分析",
            category=SkillCategory.BROWSER,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["browser", "analysis", "headless", "分析"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """Check if this is for analysis."""
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["browser_setup_for_analysis", "analysis_browser", "分析浏览器"]:
            return 1.0
        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """Execute browser setup for analysis."""
        task_data = {**task_data, "headless": True}
        return super().execute(task_data)
