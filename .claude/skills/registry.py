"""
Skill registry for managing skill discovery and registration.
"""

import importlib
import inspect
import os
from pathlib import Path
from typing import Type, Dict, List, Optional, Any, Callable

from skills.base import BaseSkill, SkillCategory, SkillMetadata
from skills.exceptions import (
    SkillNotFoundException,
    SkillRegistrationException,
)


class SkillRegistry:
    """
    Registry for managing skills.

    Handles skill registration, discovery, and retrieval.
    """

    def __init__(self):
        """Initialize the skill registry."""
        self._skills: Dict[str, Type[BaseSkill]] = {}
        self._by_category: Dict[SkillCategory, List[str]] = {
            category: [] for category in SkillCategory
        }
        self._aliases: Dict[str, str] = {}

    def register(self, skill_class: Type[BaseSkill], alias: Optional[str] = None) -> None:
        """
        Register a skill class.

        Args:
            skill_class: The skill class to register
            alias: Optional alias for the skill

        Raises:
            SkillRegistrationException: If registration fails
        """
        try:
            # Validate it's a proper skill class
            if not inspect.isclass(skill_class):
                raise SkillRegistrationException(
                    skill_class.__name__,
                    "Not a class"
                )

            if not issubclass(skill_class, BaseSkill):
                raise SkillRegistrationException(
                    skill_class.__name__,
                    "Not a subclass of BaseSkill"
                )

            # Get metadata
            try:
                metadata = skill_class.get_metadata()
            except Exception as e:
                raise SkillRegistrationException(
                    skill_class.__name__,
                    f"Failed to get metadata: {e}"
                )

            # Register the skill
            skill_name = metadata.name

            # Check for duplicate
            if skill_name in self._skills and self._skills[skill_name] != skill_class:
                raise SkillRegistrationException(
                    skill_class.__name__,
                    f"Skill name '{skill_name}' already registered by {self._skills[skill_name].__name__}"
                )

            self._skills[skill_name] = skill_class

            # Add to category index
            category = metadata.category
            if skill_name not in self._by_category[category]:
                self._by_category[category].append(skill_name)

            # Register alias if provided
            if alias:
                self._aliases[alias] = skill_name

        except SkillRegistrationException:
            raise
        except Exception as e:
            raise SkillRegistrationException(
                skill_class.__name__,
                f"Unexpected error: {e}"
            )

    def unregister(self, skill_name: str) -> bool:
        """
        Unregister a skill by name.

        Args:
            skill_name: Name of the skill to unregister

        Returns:
            bool: True if skill was unregistered
        """
        if skill_name not in self._skills:
            return False

        # Get skill class to find category
        skill_class = self._skills[skill_name]
        try:
            metadata = skill_class.get_metadata()
            category = metadata.category
            if skill_name in self._by_category[category]:
                self._by_category[category].remove(skill_name)
        except Exception:
            pass

        del self._skills[skill_name]

        # Remove aliases pointing to this skill
        self._aliases = {
            k: v for k, v in self._aliases.items()
            if v != skill_name
        }

        return True

    def get(self, skill_name: str) -> Type[BaseSkill]:
        """
        Get a skill class by name.

        Args:
            skill_name: Name of the skill (or alias)

        Returns:
            Type[BaseSkill]: The skill class

        Raises:
            SkillNotFoundException: If skill is not found
        """
        # Check alias first
        name = self._aliases.get(skill_name, skill_name)

        if name not in self._skills:
            raise SkillNotFoundException(
                skill_name,
                available_skills=list(self._skills.keys())
            )

        return self._skills[name]

    def get_instance(self, skill_name: str) -> BaseSkill:
        """
        Get a new instance of a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            BaseSkill: A new instance of the skill

        Raises:
            SkillNotFoundException: If skill is not found
        """
        skill_class = self.get(skill_name)
        return skill_class()

    def get_metadata(self, skill_name: str) -> SkillMetadata:
        """
        Get metadata for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            SkillMetadata: The skill's metadata

        Raises:
            SkillNotFoundException: If skill is not found
        """
        skill_class = self.get(skill_name)
        return skill_class.get_metadata()

    def find_best_skill(
        self,
        task_data: Dict[str, Any],
        category: Optional[SkillCategory] = None
    ) -> Optional[Type[BaseSkill]]:
        """
        Find the best skill to handle a task.

        Args:
            task_data: Task data to evaluate
            category: Optional category filter

        Returns:
            Type[BaseSkill]: The best skill class or None
        """
        candidates = self._get_candidates(category)

        if not candidates:
            return None

        best_skill = None
        best_confidence = 0.0

        for skill_name in candidates:
            skill_class = self._skills[skill_name]
            try:
                instance = skill_class()
                confidence = instance.can_handle(task_data)

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_skill = skill_class
            except Exception:
                # Skip skills that fail during can_handle
                continue

        return best_skill if best_confidence > 0 else None

    def list_skills(
        self,
        category: Optional[SkillCategory] = None,
        include_metadata: bool = False
    ) -> List[str | Dict[str, Any]]:
        """
        List registered skills.

        Args:
            category: Optional category filter
            include_metadata: If True, return full metadata

        Returns:
            List of skill names or metadata dicts
        """
        if category:
            names = self._by_category.get(category, []).copy()
        else:
            names = list(self._skills.keys())

        if not include_metadata:
            return sorted(names)

        result = []
        for name in names:
            try:
                metadata = self._skills[name].get_metadata()
                result.append({
                    "name": metadata.name,
                    "display_name": metadata.display_name,
                    "description": metadata.description,
                    "category": metadata.category.value,
                    "version": metadata.version,
                    "author": metadata.author,
                    "tags": metadata.tags,
                })
            except Exception:
                result.append({"name": name, "error": "Failed to get metadata"})
        return result

    def count(self, category: Optional[SkillCategory] = None) -> int:
        """
        Count registered skills.

        Args:
            category: Optional category filter

        Returns:
            int: Number of registered skills
        """
        if category:
            return len(self._by_category.get(category, []))
        return len(self._skills)

    def clear(self) -> None:
        """Clear all registered skills."""
        self._skills.clear()
        self._by_category = {category: [] for category in SkillCategory}
        self._aliases.clear()

    def discover_skills(
        self,
        package_path: str = "skills",
        auto_register: bool = True
    ) -> List[Type[BaseSkill]]:
        """
        Automatically discover and register skills from a package.

        Args:
            package_path: Path to the skills package
            auto_register: Whether to automatically register discovered skills

        Returns:
            List of discovered skill classes
        """
        discovered = []

        # Convert package path to file system path
        if package_path.startswith("skills"):
            base_path = Path(__file__).parent
        else:
            base_path = Path(package_path)

        # Define subpackages to search
        subpackages = [
            "question_types",
            "verification",
            "browser",
            "analysis",
        ]

        # Search in each subpackage
        for subpackage in subpackages:
            subpackage_path = base_path / subpackage
            if not subpackage_path.exists():
                continue

            for py_file in subpackage_path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                module_name = f"skills.{subpackage}.{py_file.stem}"
                discovered.extend(self._discover_from_module(module_name, auto_register))

        return discovered

    def _discover_from_module(
        self,
        module_name: str,
        auto_register: bool
    ) -> List[Type[BaseSkill]]:
        """
        Discover skills in a specific module.

        Args:
            module_name: Full module name
            auto_register: Whether to auto-register

        Returns:
            List of discovered skill classes
        """
        discovered = []

        try:
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Skip BaseSkill itself and classes from other modules
                if (obj is BaseSkill or
                    not issubclass(obj, BaseSkill) or
                    obj.__module__ != module_name):
                    continue

                discovered.append(obj)

                if auto_register:
                    try:
                        self.register(obj)
                    except SkillRegistrationException as e:
                        # Log but don't fail
                        print(f"Warning: {e}")

        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")

        return discovered

    def _get_candidates(self, category: Optional[SkillCategory]) -> List[str]:
        """Get candidate skill names filtered by category."""
        if category:
            return self._by_category.get(category, []).copy()
        return list(self._skills.keys())

    def create_index(
        self,
        key_func: Optional[Callable[[SkillMetadata], str]] = None
    ) -> Dict[str, Type[BaseSkill]]:
        """
        Create a custom index of skills.

        Args:
            key_func: Function to extract index key from metadata

        Returns:
            Dictionary mapping keys to skill classes
        """
        if key_func is None:
            key_func = lambda m: m.name

        index = {}
        for skill_name, skill_class in self._skills.items():
            try:
                metadata = skill_class.get_metadata()
                key = key_func(metadata)
                index[key] = skill_class
            except Exception:
                pass
        return index

    def __contains__(self, skill_name: str) -> bool:
        """Check if a skill is registered."""
        return skill_name in self._skills or skill_name in self._aliases

    def __len__(self) -> int:
        """Get number of registered skills."""
        return len(self._skills)

    def __iter__(self):
        """Iterate over registered skill names."""
        return iter(self._skills)


# Global default registry
_default_registry: Optional[SkillRegistry] = None


def get_default_registry() -> SkillRegistry:
    """Get or create the global default registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = SkillRegistry()
        _default_registry.discover_skills()
    return _default_registry


def reset_default_registry() -> None:
    """Reset the global default registry."""
    global _default_registry
    _default_registry = None
