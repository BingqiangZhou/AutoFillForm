"""
Verification skills for handling various verification challenges.

This module contains skills for handling:
- Intelligent verification (click-based)
- Slider verification (drag-based)
"""

from skills.verification.base import VerificationSkill
from skills.verification.intelligent import IntelligentVerificationSkill
from skills.verification.slider import SliderVerificationSkill

__all__ = [
    "VerificationSkill",
    "IntelligentVerificationSkill",
    "SliderVerificationSkill",
]
