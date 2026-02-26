"""
Matrix single choice question skill.
"""

import random
from typing import Dict, Any, List

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.question_types.base import QuestionTypeSkill


class MatrixRadioSkill(QuestionTypeSkill):
    """
    Skill for handling matrix-style single-choice questions.

    Each row (sub-question) has its own set of options with probabilities.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="matrix_radio_selection",
            display_name="矩阵单选题",
            description="处理矩阵单选题类型，每个子问题根据独立的概率权重选择选项",
            category=SkillCategory.QUESTION_TYPE,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["matrix", "matrix-radio", "矩阵", "矩阵单选"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_data contains 'probabilities_list' (list of lists)
        - task_data has 'question_type' = 'matrix' or similar
        """
        # Check for explicit type
        question_type = task_data.get("question_type", "").lower()
        if question_type in ["matrix", "matrix_radio", "矩阵", "矩阵单选"]:
            return 1.0

        # Check for probabilities_list (list of lists indicates matrix)
        if "probabilities_list" in task_data:
            value = task_data["probabilities_list"]
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], list):
                    return 0.9

        # Check for sub_questions key
        if "sub_questions" in task_data:
            return 0.85

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute matrix radio selection.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - probabilities_list: List of probability lists, one for each sub-question
                - question_index: 1-based index of the question

        Returns:
            SkillResult with success status
        """
        try:
            page = self._get_page(task_data)
            probabilities_list = task_data.get("probabilities_list", [])
            question_index = self._get_question_index(task_data)

            if not probabilities_list:
                return SkillResult.failure_result(
                    error="probabilities_list is empty"
                )

            selections = []

            # Process each sub-question
            for i, probabilities in enumerate(probabilities_list):
                if not probabilities:
                    continue

                total = sum(probabilities)
                rand = random.randint(1, total)
                cumulative = 0

                selected_index = None
                for j, prob in enumerate(probabilities):
                    cumulative += prob
                    if rand <= cumulative:
                        selected_index = j
                        break

                if selected_index is None:
                    selected_index = 0

                # Build CSS selector for matrix option
                option_id = self._build_matrix_option_id(question_index, i + 1)
                css = f"#{option_id} a[dval='{selected_index + 1}']"

                page.locator(css).click()

                selections.append({
                    "sub_question_index": i,
                    "selected_index": selected_index,
                    "css_selector": css,
                })

            return SkillResult.success_result(
                data={
                    "selections": selections,
                    "sub_question_count": len(selections),
                },
                metadata={
                    "question_index": question_index,
                    "probabilities_list": probabilities_list,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Matrix radio selection failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate matrix radio selection input."""
        if not super().validate_input(task_data):
            return False

        probabilities_list = task_data.get("probabilities_list")
        if not probabilities_list or not isinstance(probabilities_list, list):
            return False

        # Validate each sub-question's probabilities
        for probs in probabilities_list:
            if not isinstance(probs, list):
                return False
            if not all(isinstance(p, (int, float)) and p >= 0 for p in probs):
                return False

        return True
