"""
Blank filling (text input) question skill.
"""

import random
from typing import Dict, Any, List

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.question_types.base import QuestionTypeSkill


class BlankFillingSkill(QuestionTypeSkill):
    """
    Skill for handling text input (fill-in-the-blank) questions.

    Fills text input based on provided options and probabilities.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="blank_filling",
            display_name="填空题",
            description="处理填空题类型，根据文本选项和概率权重填写内容",
            category=SkillCategory.QUESTION_TYPE,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["blank", "text", "input", "fill", "填空"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_data contains 'info_list' with text_list and probabilities_list
        - task_data has 'question_type' = 'blank' or similar
        """
        # Check for explicit type
        question_type = task_data.get("question_type", "").lower()
        if question_type in ["blank", "text", "input", "fill", "填空", "填空题"]:
            return 1.0

        # Check for info_list structure [text_list, probabilities_list]
        if "info_list" in task_data:
            info_list = task_data["info_list"]
            if isinstance(info_list, list) and len(info_list) == 2:
                if isinstance(info_list[0], list) and isinstance(info_list[1], list):
                    return 0.9

        # Check for text_list directly
        if "text_list" in task_data and "probabilities_list" in task_data:
            return 0.85

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute blank filling.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - info_list: [text_list, probabilities_list] - text options and probabilities
                  OR
                - text_list: List of text options
                - probabilities_list: List of probabilities
                - question_index: 1-based index of the question

        Returns:
            SkillResult with success status
        """
        try:
            page = self._get_page(task_data)
            question_index = self._get_question_index(task_data)

            # Extract text_list and probabilities_list
            if "info_list" in task_data:
                info_list = task_data["info_list"]
                text_list = info_list[0]
                probabilities_list = info_list[1]
            else:
                text_list = task_data.get("text_list", [])
                probabilities_list = task_data.get("probabilities_list", [])

            if not text_list or not probabilities_list:
                return SkillResult.failure_result(
                    error="text_list or probabilities_list is empty"
                )

            if len(text_list) != len(probabilities_list):
                return SkillResult.failure_result(
                    error=f"text_list length ({len(text_list)}) != probabilities_list length ({len(probabilities_list)})"
                )

            # Weighted random selection
            total = sum(probabilities_list)
            rand = random.randint(1, total)
            cumulative = 0

            selected_index = None
            for j, prob in enumerate(probabilities_list):
                cumulative += prob
                if rand <= cumulative:
                    selected_index = j
                    break

            if selected_index is None:
                selected_index = 0

            # Fill the text input
            selected_text = text_list[selected_index]
            option_id = self._build_option_id(question_index, "")
            css = f"#{option_id}"

            page.locator(css).fill(selected_text)

            return SkillResult.success_result(
                data={
                    "text": selected_text,
                    "selected_index": selected_index,
                    "css_selector": css,
                },
                metadata={
                    "question_index": question_index,
                    "text_list": text_list,
                    "probabilities_list": probabilities_list,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Blank filling failed: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate blank filling input."""
        if not super().validate_input(task_data):
            return False

        # Check for info_list or separate text_list/probabilities_list
        if "info_list" in task_data:
            info_list = task_data["info_list"]
            if not isinstance(info_list, list) or len(info_list) != 2:
                return False
            text_list = info_list[0]
            probabilities_list = info_list[1]
        else:
            text_list = task_data.get("text_list")
            probabilities_list = task_data.get("probabilities_list")

        if not text_list or not probabilities_list:
            return False

        if not isinstance(text_list, list) or not isinstance(probabilities_list, list):
            return False

        if len(text_list) != len(probabilities_list):
            return False

        return all(isinstance(p, (int, float)) and p >= 0 for p in probabilities_list)
