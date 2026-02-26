"""
Browser management skills.

This module contains skills for:
- Browser setup and initialization
- Anti-detection configuration
- Browser cleanup
"""

from skills.browser.base import BrowserSkill
from skills.browser.setup import BrowserSetupSkill
from skills.browser.anti_detection import AntiDetectionSkill

__all__ = [
    "BrowserSkill",
    "BrowserSetupSkill",
    "AntiDetectionSkill",
]
