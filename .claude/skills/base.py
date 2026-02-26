"""
Core base classes for the Skills system.
Defines the fundamental interfaces that all skills must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Type, Dict, List
from datetime import datetime


class SkillCategory(Enum):
    """Categories of skills in the system."""

    QUESTION_TYPE = "question_type"
    VERIFICATION = "verification"
    BROWSER = "browser"
    ANALYSIS = "analysis"
    UTILITY = "utility"


class SkillPriority(Enum):
    """Priority levels for skill execution."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(frozen=True)
class SkillMetadata:
    """
    Metadata about a skill.

    Attributes:
        name: Unique name identifier for the skill
        display_name: Human-readable display name
        description: Detailed description of what the skill does
        category: The category this skill belongs to
        version: Skill version string
        author: Skill author
        priority: Default execution priority
        tags: List of tags for discovery
        dependencies: List of required dependencies
        config_schema: Optional schema for configuration validation
        can_handle_confidence: Default confidence threshold for can_handle
    """

    name: str
    display_name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    author: str = "AutoFillForm"
    priority: SkillPriority = SkillPriority.NORMAL
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    can_handle_confidence: float = 0.5

    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name:
            raise ValueError("Skill name cannot be empty")
        if not self.display_name:
            raise ValueError("Skill display_name cannot be empty")
        if not 0 <= self.can_handle_confidence <= 1:
            raise ValueError("can_handle_confidence must be between 0 and 1")


@dataclass
class SkillResult:
    """
    Result of a skill execution.

    Attributes:
        success: Whether the skill executed successfully
        data: Result data returned by the skill
        error: Error message if execution failed
        execution_time: Time taken to execute in seconds
        metadata: Additional metadata about the execution
        next_actions: Suggested next actions
    """

    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    next_actions: List[str] = field(default_factory=list)
    skill_name: str = ""

    @classmethod
    def success_result(cls, data: Any = None, **kwargs) -> "SkillResult":
        """Create a successful result."""
        return cls(success=True, data=data, **kwargs)

    @classmethod
    def failure_result(cls, error: str, **kwargs) -> "SkillResult":
        """Create a failure result."""
        return cls(success=False, error=error, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "next_actions": self.next_actions,
            "skill_name": self.skill_name,
        }


class BaseSkill(ABC):
    """
    Abstract base class for all skills.

    All skills must inherit from this class and implement the required methods.
    """

    _metadata: Optional[SkillMetadata] = None

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> SkillMetadata:
        """
        Return the metadata for this skill.

        Returns:
            SkillMetadata: The skill's metadata
        """
        pass

    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> float:
        """
        Determine if this skill can handle the given task.

        Args:
            task_data: Dictionary containing task information

        Returns:
            float: Confidence score between 0 and 1, where 1 means definitely can handle
        """
        pass

    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> SkillResult:
        """
        Execute the skill's main operation.

        Args:
            task_data: Dictionary containing task information

        Returns:
            SkillResult: Result of the execution
        """
        pass

    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """
        Validate input data before execution.

        Args:
            task_data: Dictionary containing task information

        Returns:
            bool: True if input is valid
        """
        return True

    def get_required_context_keys(self) -> List[str]:
        """
        Get list of required context keys for this skill.

        Returns:
            List[str]: List of required context key names
        """
        return []

    def get_optional_context_keys(self) -> List[str]:
        """
        Get list of optional context keys for this skill.

        Returns:
            List[str]: List of optional context key names
        """
        return []

    def on_before_execute(self, task_data: Dict[str, Any]) -> None:
        """
        Hook called before execution. Override for custom pre-execution logic.

        Args:
            task_data: Dictionary containing task information
        """
        pass

    def on_after_execute(self, result: SkillResult, task_data: Dict[str, Any]) -> SkillResult:
        """
        Hook called after execution. Override for custom post-execution logic.

        Args:
            result: The result from execution
            task_data: Dictionary containing task information

        Returns:
            SkillResult: Potentially modified result
        """
        return result

    def on_error(self, error: Exception, task_data: Dict[str, Any]) -> SkillResult:
        """
        Hook called when an error occurs during execution.

        Args:
            error: The exception that was raised
            task_data: Dictionary containing task information

        Returns:
            SkillResult: Error result
        """
        from skills.exceptions import SkillExecutionException
        return SkillResult.failure_result(
            error=str(error),
            skill_name=self.get_metadata().name
        )

    def __repr__(self) -> str:
        """String representation of the skill."""
        metadata = self.get_metadata()
        return f"<{self.__class__.__name__}: {metadata.name} v{metadata.version}>"


class SkillConfig:
    """
    Configuration container for skills.

    Provides type-safe access to skill configuration parameters.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize skill configuration.

        Args:
            config_dict: Dictionary of configuration parameters
        """
        self._config = config_dict or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = self._config.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        value = self._config.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = self._config.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    def get_str(self, key: str, default: str = "") -> str:
        """Get a string configuration value."""
        value = self._config.get(key, default)
        return str(value) if value is not None else default

    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """Get a list configuration value."""
        value = self._config.get(key)
        if value is None:
            return default or []
        if isinstance(value, list):
            return value
        if isinstance(value, (str, tuple)):
            return list(value)
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in configuration."""
        return key in self._config

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax."""
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax."""
        self._config[key] = value
