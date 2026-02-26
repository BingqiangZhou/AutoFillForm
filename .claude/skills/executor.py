"""
Skill executor for coordinating skill execution.
"""

import time
from typing import Any, Dict, List, Optional, Type, Union

from skills.base import BaseSkill, SkillCategory, SkillResult, SkillMetadata
from skills.context import SkillContext
from skills.exceptions import (
    SkillNotFoundException,
    SkillExecutionException,
    SkillValidationException,
    SkillContextException,
)
from skills.registry import SkillRegistry


class SkillExecutor:
    """
    Executor for coordinating skill execution.

    Handles skill invocation, validation, and lifecycle hooks.
    """

    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        context: Optional[SkillContext] = None
    ):
        """
        Initialize the skill executor.

        Args:
            registry: Skill registry to use (creates default if None)
            context: Shared skill context
        """
        if registry is None:
            from skills.registry import get_default_registry
            registry = get_default_registry()

        self.registry = registry
        self.context = context or SkillContext()
        self._execution_history: List[Dict[str, Any]] = []

    def execute_skill(
        self,
        skill_name: str,
        task_data: Dict[str, Any],
        validate: bool = True,
        raise_on_error: bool = False
    ) -> SkillResult:
        """
        Execute a specific skill by name.

        Args:
            skill_name: Name of the skill to execute
            task_data: Data to pass to the skill
            validate: Whether to validate input before execution
            raise_on_error: Whether to raise exceptions or return error results

        Returns:
            SkillResult: Result of the execution
        """
        start_time = time.time()

        try:
            # Get the skill
            skill_class = self.registry.get(skill_name)
            skill_instance = skill_class()
            metadata = skill_instance.get_metadata()

            # Prepare task data with context
            enhanced_data = self._prepare_task_data(task_data)

            # Validate context requirements
            self._validate_context(skill_instance, metadata)

            # Validate input if requested
            if validate:
                validation_errors = self._validate_input(skill_instance, enhanced_data)
                if validation_errors:
                    raise SkillValidationException(
                        skill_name,
                        validation_errors
                    )

            # Call before hook
            skill_instance.on_before_execute(enhanced_data)

            # Execute the skill
            result = skill_instance.execute(enhanced_data)

            # Call after hook
            result = skill_instance.on_after_execute(result, enhanced_data)

            # Set execution metadata
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.skill_name = skill_name

            # Record in history
            self._record_execution(skill_name, enhanced_data, result, execution_time)

            return result

        except SkillValidationException as e:
            execution_time = time.time() - start_time
            result = SkillResult.failure_result(
                error=str(e),
                execution_time=execution_time,
                skill_name=skill_name
            )
            self._record_execution(skill_name, task_data, result, execution_time)

            if raise_on_error:
                raise
            return result

        except SkillNotFoundException as e:
            execution_time = time.time() - start_time
            result = SkillResult.failure_result(
                error=str(e),
                execution_time=execution_time,
                skill_name=skill_name
            )
            self._record_execution(skill_name, task_data, result, execution_time)

            if raise_on_error:
                raise
            return result

        except Exception as e:
            execution_time = time.time() - start_time

            # Try to call error hook
            try:
                skill_instance = self.registry.get(skill_name)()
                result = skill_instance.on_error(e, task_data)
                result.execution_time = execution_time
                result.skill_name = skill_name
            except Exception:
                result = SkillResult.failure_result(
                    error=f"Unhandled error: {e}",
                    execution_time=execution_time,
                    skill_name=skill_name
                )

            self._record_execution(skill_name, task_data, result, execution_time)

            if raise_on_error:
                raise SkillExecutionException(skill_name, e, task_data)
            return result

    def execute_best_skill(
        self,
        task_data: Dict[str, Any],
        category: Optional[SkillCategory] = None,
        min_confidence: float = 0.5,
        raise_on_error: bool = False
    ) -> SkillResult:
        """
        Find and execute the best skill for a task.

        Args:
            task_data: Data to pass to the skill
            category: Optional category filter
            min_confidence: Minimum confidence threshold
            raise_on_error: Whether to raise exceptions

        Returns:
            SkillResult: Result of the execution
        """
        best_skill = self.registry.find_best_skill(task_data, category)

        if best_skill is None:
            return SkillResult.failure_result(
                error="No suitable skill found for the task"
            )

        # Verify confidence threshold
        try:
            instance = best_skill()
            confidence = instance.can_handle(task_data)
            if confidence < min_confidence:
                return SkillResult.failure_result(
                    error=f"Best skill confidence {confidence} below threshold {min_confidence}"
                )
        except Exception:
            pass

        metadata = best_skill.get_metadata()
        return self.execute_skill(
            metadata.name,
            task_data,
            raise_on_error=raise_on_error
        )

    def execute_pipeline(
        self,
        pipeline: List[Dict[str, Any]],
        stop_on_error: bool = True,
        raise_on_error: bool = False
    ) -> List[SkillResult]:
        """
        Execute a sequence of skills as a pipeline.

        Args:
            pipeline: List of pipeline steps, each with 'skill' and optional 'data' keys
            stop_on_error: Whether to stop on first error
            raise_on_error: Whether to raise exceptions

        Returns:
            List[SkillResult]: Results from each step
        """
        results = []

        for step in pipeline:
            skill_name = step.get("skill")
            step_data = step.get("data", {})

            # Merge previous results into step data if requested
            if step.get("use_previous_results") and results:
                step_data = {**step_data, "_previous_results": [r.to_dict() for r in results]}

            result = self.execute_skill(
                skill_name,
                step_data,
                raise_on_error=raise_on_error
            )
            results.append(result)

            if not result.success and stop_on_error:
                break

        return results

    def batch_execute(
        self,
        tasks: List[Dict[str, Any]],
        raise_on_error: bool = False
    ) -> List[SkillResult]:
        """
        Execute multiple tasks with their specified skills.

        Args:
            tasks: List of tasks, each with 'skill' and 'data' keys
            raise_on_error: Whether to raise exceptions

        Returns:
            List[SkillResult]: Results from each task
        """
        results = []
        for task in tasks:
            skill_name = task.get("skill")
            task_data = task.get("data", {})
            result = self.execute_skill(skill_name, task_data, raise_on_error=raise_on_error)
            results.append(result)
        return results

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history.

        Returns:
            List of execution records
        """
        return self._execution_history.copy()

    def clear_history(self) -> None:
        """Clear the execution history."""
        self._execution_history.clear()

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Dictionary with skill information or None
        """
        try:
            metadata = self.registry.get_metadata(skill_name)
            skill_class = self.registry.get(skill_name)
            instance = skill_class()

            return {
                "name": metadata.name,
                "display_name": metadata.display_name,
                "description": metadata.description,
                "category": metadata.category.value,
                "version": metadata.version,
                "author": metadata.author,
                "tags": metadata.tags,
                "priority": metadata.priority.value,
                "dependencies": metadata.dependencies,
                "required_context": instance.get_required_context_keys(),
                "optional_context": instance.get_optional_context_keys(),
            }
        except SkillNotFoundException:
            return None

    def list_available_skills(
        self,
        category: Optional[SkillCategory] = None
    ) -> List[Dict[str, Any]]:
        """
        List all available skills with their information.

        Args:
            category: Optional category filter

        Returns:
            List of skill information dictionaries
        """
        skill_names = self.registry.list_skills(category=category)
        return [self.get_skill_info(name) for name in skill_names]

    def _prepare_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare task data with context information."""
        # Add context if requested
        enhanced = task_data.copy()

        # Check if skill wants context
        if task_data.get("_include_context", False):
            enhanced["_context"] = self.context

        # Add DPI ratio if not specified
        if "dpi_ratio" not in enhanced and self.context.dpi_ratio != 1.0:
            enhanced["dpi_ratio"] = self.context.dpi_ratio

        return enhanced

    def _validate_context(self, skill: BaseSkill, metadata: SkillMetadata) -> None:
        """Validate that required context is available."""
        required_keys = skill.get_required_context_keys()
        missing_keys = []

        for key in required_keys:
            if key == "page" and not self.context.has_page():
                missing_keys.append("page")
            elif key == "browser" and not self.context.has_browser():
                missing_keys.append("browser")
            elif key not in self.context.config and not hasattr(self.context, key):
                missing_keys.append(key)

        if missing_keys:
            raise SkillContextException(
                f"Missing required context: {', '.join(missing_keys)}",
                missing_keys=missing_keys
            )

    def _validate_input(self, skill: BaseSkill, task_data: Dict[str, Any]) -> List[str]:
        """Validate skill input data."""
        errors = []

        try:
            is_valid = skill.validate_input(task_data)
            if not is_valid:
                errors.append("Input validation failed")
        except Exception as e:
            errors.append(f"Validation error: {e}")

        return errors

    def _record_execution(
        self,
        skill_name: str,
        task_data: Dict[str, Any],
        result: SkillResult,
        execution_time: float
    ) -> None:
        """Record execution in history."""
        self._execution_history.append({
            "skill_name": skill_name,
            "task_data": task_data,
            "success": result.success,
            "execution_time": execution_time,
            "timestamp": time.time(),
        })
