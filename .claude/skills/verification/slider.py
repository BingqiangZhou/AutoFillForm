"""
Slider verification skill (drag-based).
"""

from typing import Dict, Any

import pyautogui
from playwright.sync_api import Page, Locator

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.verification.base import VerificationSkill


class SliderVerificationSkill(VerificationSkill):
    """
    Skill for handling slider verification (drag-based).

    Drags the slider button from left to right to complete verification.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="slider_verification",
            display_name="滑块验证",
            description="处理滑块验证，模拟鼠标拖动滑块到最右边",
            category=SkillCategory.VERIFICATION,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.CRITICAL,
            tags=["slider", "drag", "verify", "滑块", "滑块验证"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the verification.

        Returns high confidence if:
        - task_data has 'verification_type' = 'slider'
        - locator contains slider-related elements
        """
        # Check for explicit type
        verify_type = task_data.get("verification_type", "").lower()
        if verify_type in ["slider", "drag", "滑块", "滑块验证"]:
            return 1.0

        # Check for slider selector
        if "css_selector" in task_data:
            selector = task_data["css_selector"]
            if "slide" in selector.lower() or "btn_slide" in selector:
                return 0.95

        # Check for verify text
        if "verify_text" in task_data:
            text = task_data["verify_text"]
            if "滑块" in text or "slider" in text.lower() or "drag" in text.lower():
                return 0.9

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute slider verification.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - locator: Playwright Locator for the slider element
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

            # Get slider button dimensions
            locator_btn = page.locator(".btn_slide")
            btn_box = locator_btn.bounding_box()
            btn_slide_width = btn_box['width'] * dpi_ratio / 2

            # Get slider width
            slide_box = locator.bounding_box()
            element_slide_width = slide_box['width'] * dpi_ratio

            # Move to slider button
            start_pos = (screen_x + btn_slide_width, screen_y)
            pyautogui.moveTo(start_pos)
            pyautogui.mouseDown()

            # Drag to the right
            end_x = screen_x + btn_slide_width + element_slide_width
            pyautogui.dragTo(end_x, screen_y, duration=0.5)
            pyautogui.mouseUp()

            return SkillResult.success_result(
                data={
                    "start_position": start_pos,
                    "end_position": (end_x, screen_y),
                    "drag_distance": element_slide_width,
                },
                metadata={
                    "dpi_ratio": dpi_ratio,
                    "slider_width": element_slide_width,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Slider verification failed: {e}",
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

        # Calculate window position
        window_x = 0
        window_y = 0

        # Calculate screen coordinates
        element_x = box['x']
        element_y = box['y'] - scroll_y

        # Add window position and account for DPI
        screen_x = ratio * (element_x + window_x)
        screen_y = ratio * (element_y + window_y)

        return screen_x, screen_y
