"""
Skills System - A modular, plugin-based framework for form automation.

This package provides a flexible skills system for automating survey filling,
verification handling, browser management, and survey analysis.

Example:
    >>> from skills import SkillRegistry, SkillExecutor, SkillContext
    >>> from skills.context import ContextBuilder
    >>>
    >>> # Create registry and discover skills
    >>> registry = SkillRegistry()
    >>> registry.discover_skills()
    >>>
    >>> # Create context
    >>> context = ContextBuilder().with_dpi_ratio(1.25).build()
    >>>
    >>> # Execute a skill
    >>> executor = SkillExecutor(registry, context)
    >>> result = executor.execute_skill("radio_selection", {
    ...     "probabilities": [1, 2, 3],
    ...     "question_index": 1
    ... })
"""

from skills.base import (
    BaseSkill,
    SkillCategory,
    SkillPriority,
    SkillMetadata,
    SkillResult,
    SkillConfig,
)

from skills.context import (
    SkillContext,
    ContextBuilder,
    ContextManager,
)

from skills.exceptions import (
    SkillException,
    SkillNotFoundException,
    SkillExecutionException,
    SkillValidationException,
    SkillRegistrationException,
    SkillContextException,
    SkillDependencyException,
)

from skills.registry import SkillRegistry
from skills.executor import SkillExecutor


__version__ = "1.0.0"
__author__ = "AutoFillForm"

# Public API
__all__ = [
    # Base classes
    "BaseSkill",
    "SkillCategory",
    "SkillPriority",
    "SkillMetadata",
    "SkillResult",
    "SkillConfig",
    # Context
    "SkillContext",
    "ContextBuilder",
    "ContextManager",
    # Exceptions
    "SkillException",
    "SkillNotFoundException",
    "SkillExecutionException",
    "SkillValidationException",
    "SkillRegistrationException",
    "SkillContextException",
    "SkillDependencyException",
    # Core
    "SkillRegistry",
    "SkillExecutor",
]


def create_default_registry() -> SkillRegistry:
    """
    Create a registry with all default skills registered.

    Returns:
        SkillRegistry: A registry with all skills registered
    """
    registry = SkillRegistry()
    registry.discover_skills()
    return registry


def create_executor(context: SkillContext = None) -> SkillExecutor:
    """
    Create an executor with default registry.

    Args:
        context: Optional skill context

    Returns:
        SkillExecutor: An executor ready to use
    """
    registry = create_default_registry()
    return SkillExecutor(registry, context)
