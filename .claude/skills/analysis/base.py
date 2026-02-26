"""
Base class for analysis skills.
"""

from abc import abstractmethod
from typing import Dict, Any, List

from skills.base import BaseSkill, SkillCategory, SkillMetadata, SkillResult


class AnalysisSkill(BaseSkill):
    """
    Base class for survey analysis skills.

    All analysis skills should inherit from this class.
    Provides common functionality for survey parsing and analysis.
    """

    # WJX survey element patterns
    DIV_QUESTION_ID = "divQuestion"
    FIELD_CLASS = "field"
    TOPIC_ATTR = "topic"
    TYPE_ATTR = "type"
    TOPIC_HTML_CLASS = "topichtml"
    LABEL_CLASS = "label"

    # Question type mapping
    QUESTION_TYPES = {
        '1': '填空题',
        '3': '单选题',
        '4': '多选题',
        '6': '矩阵单选题',
        '7': '下拉选择题'
    }

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this analysis skill."""
        pass

    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the analysis task.

        Returns higher confidence for matching analysis types.
        """
        pass

    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute the analysis operation.

        Args:
            task_data: Analysis parameters

        Returns:
            SkillResult with analysis data
        """
        pass

    def get_required_context_keys(self) -> List[str]:
        """Analysis skills require page access."""
        return ["page"]

    def _get_page(self, task_data: Dict[str, Any]):
        """Extract page from task data."""
        if "page" in task_data:
            return task_data["page"]
        if "_context" in task_data:
            return task_data["_context"].page
        raise ValueError("Page not found in task data")

    def _get_question_type_name(self, type_code: str) -> str:
        """Get human-readable question type name."""
        return self.QUESTION_TYPES.get(type_code, '未知类型')

    def _parse_div_for_questions(self, soup) -> List[Dict[str, Any]]:
        """
        Parse the divQuestion div for all questions.

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            List of question dictionaries
        """
        form = soup.find('div', id=self.DIV_QUESTION_ID)
        if not form:
            return []

        questions = []
        for fieldset in form.find_all('fieldset'):
            for div in fieldset.find_all('div', class_=self.FIELD_CLASS):
                question = self._parse_question_div(div)
                if question:
                    questions.append(question)

        return questions

    def _parse_question_div(self, div) -> Dict[str, Any]:
        """
        Parse a single question div.

        Args:
            div: BeautifulSoup div element

        Returns:
            Question dictionary or None
        """
        topic = div.get(self.TOPIC_ATTR)
        q_type = div.get(self.TYPE_ATTR)

        if not topic or not q_type:
            return None

        question = {
            'topic': topic,
            'type': self._get_question_type_name(q_type),
            'type_code': q_type,
        }

        # Parse question text
        topic_html = div.find('div', class_=self.TOPIC_HTML_CLASS)
        if topic_html:
            question['text'] = topic_html.text.strip()

        # Type-specific parsing
        if q_type in ['3', '4']:  # Single/Multiple choice
            question.update(self._parse_choice_options(div))
        elif q_type == '7':  # Dropdown
            question.update(self._parse_dropdown_options(div))
        elif q_type == '6':  # Matrix
            question.update(self._parse_matrix_questions(div))
        elif q_type == '1':  # Fill-in-blank
            pass  # No options to parse

        return question

    def _parse_choice_options(self, div) -> Dict[str, Any]:
        """Parse options for single/multiple choice questions."""
        options = []
        for label in div.find_all('div', class_=self.LABEL_CLASS):
            options.append(label.text.strip())
        return {
            'options': options,
            'option_count': len(options),
        }

    def _parse_dropdown_options(self, div) -> Dict[str, Any]:
        """Parse options for dropdown questions."""
        options = []
        select_el = div.find('select')
        if select_el:
            for option in select_el.find_all('option'):
                val = option.get('value', '').strip()
                if val:  # Filter empty placeholder options
                    options.append(option.text.strip())
        return {
            'options': options,
            'option_count': len(options),
        }

    def _parse_matrix_questions(self, div) -> Dict[str, Any]:
        """Parse sub-questions and options for matrix questions."""
        sub_questions = []
        for row in div.find_all('tr', class_='rowtitle'):
            sub_question = row.find('span', class_='itemTitleSpan')
            if not sub_question:
                continue

            sub_q_text = sub_question.text.strip()
            options = []
            next_row = row.find_next_sibling('tr')
            if next_row:
                for opt in next_row.find_all('a'):
                    options.append(opt.get('dval'))

            sub_questions.append({
                'sub_question': sub_q_text,
                'options': options,
                'option_count': len(options)
            })

        return {
            'sub_questions': sub_questions,
            'sub_question_count': len(sub_questions),
        }
