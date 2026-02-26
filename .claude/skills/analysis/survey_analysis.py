"""
Survey analysis skill for parsing survey pages.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup

from skills.base import SkillCategory, SkillMetadata, SkillResult, SkillPriority
from skills.analysis.base import AnalysisSkill


class SurveyAnalysisSkill(AnalysisSkill):
    """
    Skill for analyzing survey pages and extracting question information.

    Parses HTML content to identify questions, their types, and options.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="survey_analysis",
            display_name="问卷分析",
            description="分析问卷页面结构，提取题目信息、类型和选项",
            category=SkillCategory.ANALYSIS,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["survey", "analysis", "parse", "问卷", "分析"],
            can_handle_confidence=0.9,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the task.

        Returns high confidence if:
        - task_type is 'survey_analysis' or similar
        - task_data contains 'page' or 'html_content'
        """
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["survey_analysis", "analyze_survey", "问卷分析"]:
            return 1.0

        if "page" in task_data or "html_content" in task_data:
            return 0.7

        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute survey analysis.

        Args:
            task_data: Must contain:
                - page: Playwright Page instance (to get content)
                  OR
                - html_content: Direct HTML content to parse

        Returns:
            SkillResult with parsed questions
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
            questions = self._parse_div_for_questions(soup)

            if not questions:
                return SkillResult.failure_result(
                    error="No questions found in the survey page",
                    metadata={"page_content_length": len(page_content)}
                )

            return SkillResult.success_result(
                data={
                    "questions": questions,
                    "question_count": len(questions),
                },
                metadata={
                    "question_types": self._count_question_types(questions),
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Survey analysis failed: {e}",
                skill_name=self.get_metadata().name
            )

    def _count_question_types(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count questions by type."""
        type_counts = {}
        for q in questions:
            q_type = q.get('type', 'unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        return type_counts


class GotoSurveySkill(AnalysisSkill):
    """
    Skill for navigating to a survey URL and waiting for page load.
    """

    @classmethod
    def get_metadata(cls) -> SkillMetadata:
        """Return the metadata for this skill."""
        return SkillMetadata(
            name="goto_survey",
            display_name="打开问卷",
            description="导航到问卷URL并等待页面加载完成",
            category=SkillCategory.ANALYSIS,
            version="1.0.0",
            author="AutoFillForm",
            priority=SkillPriority.HIGH,
            tags=["survey", "goto", "navigate", "打开"],
            can_handle_confidence=0.8,
        )

    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """Check if this is a navigation task."""
        task_type = task_data.get("task_type", "").lower()
        if task_type in ["goto_survey", "navigate", "open_survey", "打开问卷"]:
            return 1.0
        if "url" in task_data:
            return 0.6
        return 0.0

    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """Navigate to survey URL."""
        try:
            page = self._get_page(task_data)
            url = task_data.get("url", "")

            if not url:
                return SkillResult.failure_result(
                    error="url is required"
                )

            wait_until = task_data.get("wait_until", "domcontentloaded")
            timeout = task_data.get("timeout", 30000)

            page.goto(url, wait_until=wait_until, timeout=timeout)

            # Wait for question div to appear
            wait_for_selector = task_data.get("wait_for_selector", f"#{self.DIV_QUESTION_ID}")
            page.wait_for_selector(wait_for_selector, timeout=10000)

            return SkillResult.success_result(
                data={
                    "url": url,
                    "title": page.title(),
                },
                metadata={
                    "wait_until": wait_until,
                    "timeout": timeout,
                }
            )

        except Exception as e:
            return SkillResult.failure_result(
                error=f"Failed to navigate to survey: {e}",
                skill_name=self.get_metadata().name
            )

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """Validate navigation input."""
        return "url" in task_data
