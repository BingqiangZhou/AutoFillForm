"""
Base class for verification skills.
"""

from abc import abstractmethod
from typing import Dict, Any, List

from skills.base import BaseSkill, SkillCategory, SkillMetadata, SkillResult


class VerificationSkill(BaseSkill):
    """
    Base class for verification handling skills.

    All verification skills should inherit from this class.
    Provides common functionality for verification challenges.
    """

    # Common verification elements
    INTELLIGENT_VERIFY_TEXT = "点击按钮开始智能验证"
    SLIDER_VERIFY_TEXT = "请按住滑块，拖动到最右边"
    SMART_TXT_SELECTOR = ".sm-txt"
    SLIDER_SELECTOR = "span.btn_slide"

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this verification skill."""
        pass

    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the verification.

        Returns higher confidence for matching verification types.
        """
        pass

    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute the verification handling operation.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - locator or verification element info
                - dpi_ratio: Windows DPI scaling ratio

        Returns:
            SkillResult with success status
        """
        pass

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate common input for verification skills."""
        # Page is required
        if "page" not in task_data:
            return False

        # Either locator or selector info is needed
        return "locator" in task_data or "css_selector" in task_data

    def get_required_context_keys(self) -> List[str]:
        """Verification skills require page and may need DPI ratio."""
        return ["page"]

    def get_optional_context_keys(self) -> List[str]:
        """Verification skills optionally use DPI ratio."""
        return ["dpi_ratio"]

    def _get_page(self, task_data: Dict[str, Any]):
        """Extract page from task data."""
        if "page" in task_data:
            return task_data["page"]
        if "_context" in task_data:
            return task_data["_context"].page
        raise ValueError("Page not found in task data")

    def _get_dpi_ratio(self, task_data: Dict[str, Any]) -> float:
        """Extract DPI ratio from task data."""
        if "dpi_ratio" in task_data:
            return task_data["dpi_ratio"]
        if "_context" in task_data:
            return task_data["_context"].dpi_ratio
        return 1.0

    def _get_locator(self, task_data: Dict[str, Any]):
        """Extract locator from task data."""
        if "locator" in task_data:
            return task_data["locator"]
        # If CSS selector is provided, return it for the skill to use
        if "css_selector" in task_data:
            return task_data["css_selector"]
        return None
