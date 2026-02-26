"""
Survey analysis skills.

This module contains skills for:
- Survey page analysis
- Question type detection
- HTML parsing
"""

from skills.analysis.base import AnalysisSkill
from skills.analysis.survey_analysis import SurveyAnalysisSkill
from skills.analysis.question_detection import QuestionDetectionSkill

__all__ = [
    "AnalysisSkill",
    "SurveyAnalysisSkill",
    "QuestionDetectionSkill",
]
