"""
Question detection skill for identifying question types.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.analysis.base import AnalysisSkill


class QuestionDetectionSkill(AnalysisSkill):
    """
    Skill for detecting question types and elements on a survey page.

    Identifies the type of each question and provides CSS selectors for interaction.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="question_detection",
            display_name="题型检测",
            description="检测问卷题目类型，提供交互所需的CSS选择器",
            category=SkillCategory.ANALYSIS,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.NORMAL,
            tags=["detection", "question-type", "检测", "题型"],
            can_handle_confidence=0.8,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_type is 'question_detection' or similar
        - task_data contains 'question_index' for specific question detection
        """
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["question_detection", "detect_question_type", "题型检测"]:
            return 1.0

        if "question_index" in task_data:
            return 0.7

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute question type detection.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance
                - question_index: (Optional) Index of specific question to detect
                  OR
                - html_content: Direct HTML content to parse

        Returns:
            SkillResult with detected question types and selectors
        """
        try:
            # Get HTML content
            if "html_content" in task_data:
                page_content = task_data["html_content"]
            else:
                page = self._get_page(task_data)
                page_content = page.content()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_content, 'html.parser')

            # Check for specific question or all questions
            question_index = task_data.get("question_index")

            if question_index is not None:
                result = self._detect_single_question(soup, question_index)
            else:
                result = self._detect_all_questions(soup)

            return SkillResult.success_result(
                data=result,
                metadata={
                    "detection_type": "single" if question_index else "all",
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Question detection failed: {e}",
                skill_name=self.get_metadata().name
            )

    def _detect_all_questions(self, soup) -> List[Dict[str, Any]]:
        """Detect all questions on the page."""
        form = soup.find('div', id=self.DIV_QUESTION_ID)
        if not form:
            return []

        questions = []
        for idx, fieldset in enumerate(form.find_all('fieldset'), 1):
            for div in fieldset.find_all('div', class_=self.FIELD_CLASS):
                q_type = div.get(self.TYPE_ATTR)
                if not q_type:
                    continue

                detected = {
                    'question_index': idx,
                    'type_code': q_type,
                    'type_name': self._get_question_type_name(q_type),
                    'selectors': self._get_selectors_for_type(q_type, idx),
                }

                # Add topic info
                topic = div.get(self.TOPIC_ATTR)
                if topic:
                    detected['topic'] = topic

                # Get text
                topic_html = div.find('div', class_=self.TOPIC_HTML_CLASS)
                if topic_html:
                    detected['text'] = topic_html.text.strip()

                questions.append(detected)

        return questions

    def _detect_single_question(self, soup, question_index: int) -> Dict[str, Any]:
        """Detect a specific question by index."""
        form = soup.find('div', id=self.DIV_QUESTION_ID)
        if not form:
            return {"error": "Question div not found"}

        current_idx = 0
        for fieldset in form.find_all('fieldset'):
            for div in fieldset.find_all('div', class_=self.FIELD_CLASS):
                current_idx += 1
                if current_idx == question_index:
                    q_type = div.get(self.TYPE_ATTR)
                    if not q_type:
                        return {"error": f"Question {question_index} has no type"}

                    detected = {
                        'question_index': question_index,
                        'type_code': q_type,
                        'type_name': self._get_question_type_name(q_type),
                        'selectors': self._get_selectors_for_type(q_type, question_index),
                    }

                    # Add topic info
                    topic = div.get(self.TOPIC_ATTR)
                    if topic:
                        detected['topic'] = topic

                    # Get text
                    topic_html = div.find('div', class_=self.TOPIC_HTML_CLASS)
                    if topic_html:
                        detected['text'] = topic_html.text.strip()

                    return detected

        return {"error": f"Question {question_index} not found"}

    def _get_selectors_for_type(self, q_type: str, question_index: int) -> Dict[str, str]:
        """Get CSS selectors for a question type."""
        selectors = {
            'question_id': f'q{question_index}',
        }

        if q_type == '3':  # Radio
            selectors['input_type'] = 'radio'
            selectors['option_selector'] = 'a.jqradio'
        elif q_type == '4':  # Checkbox
            selectors['input_type'] = 'checkbox'
            selectors['option_selector'] = 'a.jqcheck'
        elif q_type == '6':  # Matrix
            selectors['input_type'] = 'matrix'
            selectors['option_selector'] = 'a[dval]'
        elif q_type == '1':  # Text input
            selectors['input_type'] = 'text'
            selectors['option_selector'] = 'input[type="text"]'
        elif q_type == '7':  # Select
            selectors['input_type'] = 'select'
            selectors['option_selector'] = 'option'

        return selectors


class QuestionCountSkill(AnalysisSkill):
    """
    Skill for counting the number of questions on a survey page.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="question_count",
            display_name="题目计数",
            description="统计问卷页面上的题目数量",
            category=SkillCategory.ANALYSIS,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.LOW,
            tags=["count", "question", "统计"],
            can_handle_confidence=0.7,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """Check if this is a count task."""
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["question_count", "count_questions", "题目计数"]:
            return 1.0
        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """Count questions on the page."""
        try:
            if "html_content" in task_data:
                page_content = task_data["html_content"]
            else:
                page = self._get_page(task_data)
                page_content = page.content()

            soup = BeautifulSoup(page_content, 'html.parser')
            form = soup.find('div', id=self.DIV_QUESTION_ID)

            if not form:
                return SkillResult.failure_result(
                    error="Question div not found"
                )

            count = 0
            for fieldset in form.find_all('fieldset'):
                count += len(fieldset.find_all('div', class_=self.FIELD_CLASS))

            return SkillResult.success_result(
                data={
                    "question_count": count,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Question count failed: {e}",
                skill_name=self.get_metadata().name
            )
