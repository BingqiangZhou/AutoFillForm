"""
Anti-detection configuration skill.
"""

from typing import Dict, Any

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.browser.base import BrowserSkill


class AntiDetectionSkill(BrowserSkill):
    """
    Skill for applying anti-detection measures to browser context.

    Adds scripts and settings to make browser automation less detectable.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="anti_detection",
            display_name="反检测配置",
            description="应用反检测脚本和配置，降低浏览器自动化检测风险",
            category=SkillCategory.BROWSER,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.NORMAL,
            tags=["anti-detection", "stealth", "反检测"],
            can_handle_confidence=0.8,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_type is 'anti_detection' or similar
        - task_data contains 'context' that needs anti-detection
        """
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["anti_detection", "anti_detection_config", "反检测"]:
            return 1.0

        if "context" in task_data and task_data.get("apply_anti_detection"):
            return 0.9

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute anti-detection configuration.

        Args:
            task_data: Must contain:
                - context: Playwright BrowserContext to configure

        Returns:
            SkillResult with success status
        """
        try:
            context = task_data.get("context")

            if context is None:
                return SkillResult.failure_result(
                    error="context is required"
                )

            # Apply anti-detection scripts
            self._apply_anti_detection(context)

            # Additional anti-detection measures
            user_agent = task_data.get("user_agent", self.DEFAULT_USER_AGENT)
            locale = task_data.get("locale", self.DEFAULT_LOCALE)

            return SkillResult.success_result(
                data={
                    "anti_detection_applied": True,
                },
                metadata={
                    "user_agent": user_agent,
                    "locale": locale,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Anti-detection configuration failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate anti-detection input."""
        return "context" in task_data


class BrowserCleanupSkill(BrowserSkill):
    """
    Skill for cleaning up browser resources.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="browser_cleanup",
            display_name="浏览器清理",
            description="清理浏览器资源，关闭页面、上下文和浏览器实例",
            category=SkillCategory.BROWSER,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.NORMAL,
            tags=["cleanup", "close", "清理"],
            can_handle_confidence=0.8,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_type is 'browser_cleanup' or similar
        - task_data contains browser resources to cleanup
        """
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["browser_cleanup", "cleanup", "close_browser", "清理"]:
            return 1.0

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute browser cleanup.

        Args:
            task_data: May contain:
                - page: Page to close
                - context: Context to close
                - browser: Browser to close
                - playwright_instance: Playwright instance to stop

        Returns:
            SkillResult with success status
        """
        try:
            closed_resources = []

            # Close page
            page = task_data.get("page")
            if page:
                try:
                    page.close()
                    closed_resources.append("page")
                except Exception:
                    pass

            # Close context
            context = task_data.get("context")
            if context:
                try:
                    context.close()
                    closed_resources.append("context")
                except Exception:
                    pass

            # Close browser
            browser = task_data.get("browser")
            if browser:
                try:
                    browser.close()
                    closed_resources.append("browser")
                except Exception:
                    pass

            # Stop playwright
            playwright_instance = task_data.get("playwright_instance")
            if playwright_instance:
                try:
                    playwright_instance.stop()
                    closed_resources.append("playwright_instance")
                except Exception:
                    pass

            return SkillResult.success_result(
                data={
                    "closed_resources": closed_resources,
                },
                metadata={
                    "cleanup_complete": True,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Browser cleanup failed: {e}",
                skill_name=self.get_metadata().name
            )
