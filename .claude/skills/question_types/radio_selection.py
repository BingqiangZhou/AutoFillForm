"""
Radio button (single choice) question skill.
"""

import random
from typing import Dict, Any

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.question_types.base import QuestionTypeSkill


class RadioSelectionSkill(QuestionTypeSkill):
    """
    Skill for handling single-choice (radio button) questions.

    Selects one option from a list based on weighted probabilities.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="radio_selection",
            display_name="单选题",
            description="处理单选题（单选按钮）类型的题目，根据概率权重选择一个选项",
            category=SkillCategory.QUESTION_TYPE,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["radio", "single-choice", "单选"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_data contains 'probabilities' key
        - task_data has 'question_type' = 'radio' or similar
        """
        # Check for explicit type
        question_type = task_data.get("question_type", "").lower()
        if question_type in ["radio", "radio_selection", "single", "单选"]:
            return 1.0

        # Check for probabilities (common for radio)
        if "probabilities" in task_data:
            return 0.8

        # Check for WJX radio selector
        if "css_selector" in task_data:
            selector = task_data["css_selector"]
            if "jqradio" in selector:
                return 0.95

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute radio button selection.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - probabilities: List of probability weights for each option
                - question_index: 1-based index of the question

        Returns:
            SkillResult with success status
        """
        try:
            page = self._get_page(task_data)
            probabilities = task_data.get("probabilities", [])
            question_index = self._get_question_index(task_data)

            if not probabilities:
                return SkillResult.failure_result(
                    error="probabilities list is empty"
                )

            # Weighted random selection
            total = sum(probabilities)
            rand = random.randint(1, total)
            cumulative = 0

            selected_index = None
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if rand <= cumulative:
                    selected_index = i
                    break

            if selected_index is None:
                selected_index = 0

            # Build CSS selector and click
            option_id = self._build_option_id(question_index, selected_index + 1)
            css = f"#{option_id} + a.jqradio"

            page.locator(css).click()

            return SkillResult.success_result(
                data={
                    "option_id": option_id,
                    "selected_index": selected_index,
                    "css_selector": css,
                },
                metadata={
                    "question_index": question_index,
                    "probabilities": probabilities,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Radio selection failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate radio selection input."""
        if not super().validate_input(task_data):
            return False

        probabilities = task_data.get("probabilities")
        if not probabilities or not isinstance(probabilities, list):
            return False

        return all(isinstance(p, (int, float)) and p >= 0 for p in probabilities)
