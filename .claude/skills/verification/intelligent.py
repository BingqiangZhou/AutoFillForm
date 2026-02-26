"""
Intelligent verification skill (click-based).
"""

from typing import Dict, Any

import pyautogui
from playwright.sync_api import Page, Locator

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.verification.base import VerificationSkill


class IntelligentVerificationSkill(VerificationSkill):
    """
    Skill for handling intelligent verification (click-based).

    Clicks on the verification element at its screen position.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="intelligent_verification",
            display_name="智能验证",
            description="处理智能验证（点击按钮），使用屏幕坐标模拟鼠标点击",
            category=SkillCategory.VERIFICATION,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.CRITICAL,
            tags=["intelligent", "click", "verify", "智能验证"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the verification.

        Returns high confidence if:
        - task_data has 'verification_type' = 'intelligent'
        - locator contains '.sm-txt' with intelligent verification text
        """
        # Check for explicit type
        verify_type = task_data.get("verification_type", "").lower()
        if verify_type in ["intelligent", "click", "智能", "智能验证"]:
            return 1.0

        # Check for intelligent verification selector
        if "css_selector" in task_data:
            selector = task_data["css_selector"]
            if "sm-txt" in selector:
                return 0.95

        # Check for text content
        if "verify_text" in task_data:
            text = task_data["verify_text"]
            if "智能验证" in text or "intelligent" in text.lower():
                return 0.9

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute intelligent verification.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - locator: Playwright Locator for the verification element
                - dpi_ratio: Windows DPI scaling ratio

        Returns:
            SkillResult with success status
        """
        try:
            page = self._get_page(task_data)
            locator = task_data.get("locator")
            dpi_ratio = self._get_dpi_ratio(task_data)

            if locator is None:
                return SkillResult.failure_result(
                    error="locator is required"
                )

            # Get screen coordinates
            screen_x, screen_y = self._get_element_screen_pos(page, locator, dpi_ratio)

            # Click at the position
            click_pos = (screen_x, screen_y)
            pyautogui.click(click_pos)

            return SkillResult.success_result(
                data={
                    "click_position": click_pos,
                    "screen_x": screen_x,
                    "screen_y": screen_y,
                },
                metadata={
                    "dpi_ratio": dpi_ratio,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Intelligent verification failed: {e}",
                skill_name=self.get_metadata().name
            )

    def _get_element_screen_pos(
        self,
        page: Page,
        locator: Locator,
        ratio: float
    ) -> tuple:
        """
        Get the screen coordinates of an element, accounting for DPI scaling.

        Args:
            page: Playwright Page instance
            locator: Playwright Locator
            ratio: Windows DPI scaling ratio

        Returns:
            tuple: (screen_x, screen_y) coordinates
        """
        # Get element bounding box
        box = locator.bounding_box()

        # Get viewport size
        viewport_size = page.viewport_size

        # Get page scroll position
        scroll_y = page.evaluate("window.pageYOffset")

        # Calculate window position (approximate for Playwright)
        window_x = 0
        window_y = 0

        # Calculate screen coordinates
        element_x = box['x']
        element_y = box['y'] - scroll_y

        # Add window position and account for DPI
        screen_x = ratio * (element_x + window_x)
        screen_y = ratio * (element_y + window_y)

        return screen_x, screen_y
