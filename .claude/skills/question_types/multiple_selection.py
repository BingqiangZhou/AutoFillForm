"""
Multiple choice (checkbox) question skill.
"""

import random
from typing import Dict, Any

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.question_types.base import QuestionTypeSkill


class MultipleSelectionSkill(QuestionTypeSkill):
    """
    Skill for handling multiple-choice (checkbox) questions.

    Selects multiple options based on individual probabilities.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="multiple_selection",
            display_name="多选题",
            description="处理多选题（复选框）类型的题目，每个选项根据独立概率决定是否选中",
            category=SkillCategory.QUESTION_TYPE,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["multiple", "checkbox", "multi-choice", "多选"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_data contains 'probabilities' with percentages (0-100)
        - task_data has 'question_type' = 'multiple' or similar
        """
        # Check for explicit type
        question_type = task_data.get("question_type", "").lower()
        if question_type in ["multiple", "multiple_selection", "checkbox", "multi", "多选"]:
            return 1.0

        # Check for jqcheckbox selector
        if "css_selector" in task_data:
            selector = task_data["css_selector"]
            if "jqcheck" in selector or "checkbox" in selector:
                return 0.95

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute multiple choice selection.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - probabilities: List of probability percentages (0-100) for each option
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

            selected_indices = []

            # Select options based on individual probabilities
            for i, prob in enumerate(probabilities):
                if random.randint(1, 100) <= prob:
                    option_id = self._build_option_id(question_index, i + 1)
                    css = f"#{option_id} + a.jqcheck"
                    page.locator(css).click()
                    selected_indices.append(i)

            # If no options selected, choose the one with highest probability
            if not selected_indices:
                max_value = max(probabilities)
                max_index = probabilities.index(max_value)
                option_id = self._build_option_id(question_index, max_index + 1)
                css = f"#{option_id} + a.jqcheck"
                page.locator(css).click()
                selected_indices.append(max_index)

            return SkillResult.success_result(
                data={
                    "selected_indices": selected_indices,
                    "selected_count": len(selected_indices),
                },
                metadata={
                    "question_index": question_index,
                    "probabilities": probabilities,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Multiple selection failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate multiple selection input."""
        if not super().validate_input(task_data):
            return False

        probabilities = task_data.get("probabilities")
        if not probabilities or not isinstance(probabilities, list):
            return False

        return all(isinstance(p, (int, float)) and 0 <= p <= 100 for p in probabilities)
