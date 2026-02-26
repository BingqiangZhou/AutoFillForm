"""
Base class for question type skills.
"""

from abc import abstractmethod
from typing import Dict, Any, List

from skills.base import BaseSkill, SkillCategory, SkillMetadata, SkillResult


class QuestionTypeSkill(BaseSkill):
    """
    Base class for question type skills.

    All question handling skills should inherit from this class.
    Provides common functionality for form filling operations.
    """

    # Common CSS selectors and patterns
    QUESTION_PREFIX = "q"
    MATRIX_PREFIX = "drv"
    RADIO_SELECTOR = "a.jqradio"
    CHECKBOX_SELECTOR = "a.jqcheck"

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this question type skill."""
        pass

    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the given question.

        Returns higher confidence for matching question types.
        """
        pass

    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute the question filling operation.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - question_index: 1-based index of the question
                - Additional type-specific parameters

        Returns:
            SkillResult with success status
        """
        pass

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate common input for question type skills."""
        required_keys = ["page", "question_index"]
        return all(key in task_data for key in required_keys)

    def get_required_context_keys(self) -> List[str]:
        """Question type skills require a page context."""
        return ["page"]

    def _build_option_id(self, question_index: int, option_index: int) -> str:
        """Build the standard option ID for a question."""
        return f"{self.QUESTION_PREFIX}{question_index}_{option_index}"

    def _build_matrix_option_id(self, question_index: int, sub_question_index: int) -> str:
        """Build the matrix option ID for a question."""
        return f"{self.MATRIX_PREFIX}{question_index}_{sub_question_index}"

    def _get_page(self, task_data: Dict[str, Any]):
        """Extract page from task data, supporting both direct and context access."""
        if "page" in task_data:
            return task_data["page"]
        if "_context" in task_data:
            return task_data["_context"].page
        raise ValueError("Page not found in task data")

    def _get_question_index(self, task_data: Dict[str, Any]) -> int:
        """Extract and validate question index from task data."""
        index = task_data.get("question_index", 1)
        if not isinstance(index, int) or index < 1:
            raise ValueError("question_index must be a positive integer")
        return index
