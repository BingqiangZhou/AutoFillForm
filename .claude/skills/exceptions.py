"""
Skills system exception classes.
Defines all custom exceptions used in the skills framework.
"""

from typing import Optional, Any


class SkillException(Exception):
    """Base exception for all skill-related errors."""

    def __init__(self, message: str, skill_name: Optional[str] = None, details: Optional[dict] = None):
        """
        Initialize a skill exception.

        Args:
            message: Error message
            skill_name: Name of the skill that raised the exception
            details: Additional details about the error
        """
        self.skill_name = skill_name
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.skill_name:
            return f"[{self.skill_name}] {base_msg}"
        return base_msg


class SkillNotFoundException(SkillException):
    """Raised when a requested skill is not found in the registry."""

    def __init__(self, skill_name: str, available_skills: Optional[list[str]] = None):
        """
        Initialize skill not found exception.

        Args:
            skill_name: Name of the skill that was not found
            available_skills: List of available skill names
        """
        self.available_skills = available_skills or []
        self.skill_name = skill_name
        message = f"Skill '{skill_name}' not found"
        if self.available_skills:
            message += f". Available skills: {', '.join(self.available_skills)}"
        super().__init__(message, skill_name=skill_name)


class SkillExecutionException(SkillException):
    """Raised when a skill fails during execution."""

    def __init__(
        self,
        skill_name: str,
        original_exception: Optional[Exception] = None,
        task_data: Optional[dict] = None
    ):
        """
        Initialize skill execution exception.

        Args:
            skill_name: Name of the skill that failed
            original_exception: The original exception that caused the failure
            task_data: Task data that was being processed
        """
        self.original_exception = original_exception
        self.task_data = task_data or {}
        message = f"Skill '{skill_name}' execution failed"
        if original_exception:
            message += f": {original_exception}"
        super().__init__(message, skill_name=skill_name, details=task_data)


class SkillValidationException(SkillException):
    """Raised when skill input validation fails."""

    def __init__(self, skill_name: str, validation_errors: list[str]):
        """
        Initialize skill validation exception.

        Args:
            skill_name: Name of the skill
            validation_errors: List of validation error messages
        """
        self.validation_errors = validation_errors
        message = f"Skill '{skill_name}' validation failed: {'; '.join(validation_errors)}"
        super().__init__(message, skill_name=skill_name, details={'errors': validation_errors})


class SkillRegistrationException(SkillException):
    """Raised when skill registration fails."""

    def __init__(self, skill_class_name: str, reason: str):
        """
        Initialize skill registration exception.

        Args:
            skill_class_name: Name of the skill class
            reason: Reason why registration failed
        """
        self.skill_class_name = skill_class_name
        message = f"Failed to register skill '{skill_class_name}': {reason}"
        super().__init__(message, skill_name=skill_class_name)


class SkillContextException(SkillException):
    """Raised when skill context is invalid or missing required data."""

    def __init__(self, message: str, missing_keys: Optional[list[str]] = None):
        """
        Initialize skill context exception.

        Args:
            message: Error message
            missing_keys: List of missing context keys
        """
        self.missing_keys = missing_keys or []
        details = {'missing_keys': missing_keys} if missing_keys else None
        super().__init__(message, details=details)


class SkillDependencyException(SkillException):
    """Raised when a skill's dependencies cannot be resolved."""

    def __init__(self, skill_name: str, missing_dependencies: list[str]):
        """
        Initialize skill dependency exception.

        Args:
            skill_name: Name of the skill with unmet dependencies
            missing_dependencies: List of missing dependencies
        """
        self.missing_dependencies = missing_dependencies
        message = f"Skill '{skill_name}' has unmet dependencies: {', '.join(missing_dependencies)}"
        super().__init__(message, skill_name=skill_name, details={'dependencies': missing_dependencies})
