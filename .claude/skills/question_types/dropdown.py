"""
Dropdown (select) question skill.
"""

import random
from typing import Dict, Any, List

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.question_types.base import QuestionTypeSkill


class DropdownSkill(QuestionTypeSkill):
    """
    Skill for handling dropdown (select) questions.

    Selects an option from a dropdown based on weighted probabilities.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="dropdown_selection",
            display_name="下拉选择题",
            description="处理下拉选择题类型，根据概率权重选择下拉框中的一个选项",
            category=SkillCategory.QUESTION_TYPE,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["dropdown", "select", "choice", "下拉", "下拉选择"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_data contains 'options' list (common for dropdown)
        - task_data has 'question_type' = 'dropdown' or similar
        """
        # Check for explicit type
        question_type = task_data.get("question_type", "").lower()
        if question_type in ["dropdown", "select", "selection", "下拉", "下拉选择", "下拉框"]:
            return 1.0

        # Check for select selector
        if "css_selector" in task_data:
            selector = task_data["css_selector"]
            if "select" in selector.lower():
                return 0.9

        # Check for options with probabilities (dropdown style)
        if "options" in task_data and "probabilities" in task_data:
            return 0.7

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute dropdown selection.

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

            # WJX dropdown option value starts from 1
            css = f"#q{question_index}"
            page.locator(css).select_option(value=str(selected_index + 1))

            return SkillResult.success_result(
                data={
                    "selected_index": selected_index,
                    "selected_value": str(selected_index + 1),
                    "css_selector": css,
                },
                metadata={
                    "question_index": question_index,
                    "probabilities": probabilities,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Dropdown selection failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate dropdown selection input."""
        if not super().validate_input(task_data):
            return False

        probabilities = task_data.get("probabilities")
        if not probabilities or not isinstance(probabilities, list):
            return False

        return all(isinstance(p, (int, float)) and p >= 0 for p in probabilities)
