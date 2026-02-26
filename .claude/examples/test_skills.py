#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skills System Unit Tests

Tests for the Skills system components.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills import (
    SkillRegistry,
    SkillExecutor,
    SkillContext,
    ContextBuilder,
)
from skills.base import SkillCategory, SkillResult


def test_registry_discovery():
    """Test skill registry discovery."""
    print("\n[TEST] Registry Discovery")

    registry = SkillRegistry()
    count = registry.count()
    print(f"  Initial count: {count}")

    registry.discover_skills()
    new_count = registry.count()
    print(f"  After discovery: {new_count}")

    assert new_count > count, "Skills should be discovered"
    print(f"  [OK] Discovered {new_count - count} skills")

    return True


def test_skill_metadata():
    """Test skill metadata access."""
    print("\n[TEST] Skill Metadata")

    registry = SkillRegistry()
    registry.discover_skills()

    for skill_name in ["radio_selection", "intelligent_verification", "browser_setup"]:
        if skill_name in registry:
            metadata = registry.get_metadata(skill_name)
            print(f"  {metadata.name}: {metadata.display_name}")
            assert metadata.name == skill_name
            assert metadata.version
            print(f"    [OK] Version {metadata.version}")

    return True


def test_skill_can_handle():
    """Test skill can_handle method."""
    print("\n[TEST] Skill can_handle")

    registry = SkillRegistry()
    registry.discover_skills()

    # Test radio selection skill
    radio_skill = registry.get_instance("radio_selection")
    confidence = radio_skill.can_handle({
        "probabilities": [1, 2, 3],
        "question_index": 1
    })
    print(f"  Radio selection confidence: {confidence}")
    assert confidence > 0, "Should recognize radio task"

    # Test intelligent verification skill
    verify_skill = registry.get_instance("intelligent_verification")
    confidence = verify_skill.can_handle({
        "verification_type": "intelligent"
    })
    print(f"  Intelligent verification confidence: {confidence}")
    assert confidence > 0, "Should recognize verification task"

    return True


def test_skill_validation():
    """Test skill input validation."""
    print("\n[TEST] Skill Validation")

    registry = SkillRegistry()
    registry.discover_skills()

    radio_skill = registry.get_instance("radio_selection")

    # Valid input
    valid = radio_skill.validate_input({
        "page": "mock_page",
        "probabilities": [1, 2, 3],
        "question_index": 1
    })
    print(f"  Valid input: {valid}")
    assert valid, "Should validate correct input"

    # Invalid input
    invalid = radio_skill.validate_input({
        "probabilities": [1, 2, 3]
    })
    print(f"  Invalid input: {invalid}")
    assert not invalid, "Should reject incorrect input"

    return True


def test_context_builder():
    """Test context builder."""
    print("\n[TEST] Context Builder")

    context = (ContextBuilder()
               .with_dpi_ratio(1.25)
               .with_state({"test": "value"})
               .build())

    print(f"  DPI ratio: {context.dpi_ratio}")
    print(f"  State: {context.state}")

    assert context.dpi_ratio == 1.25
    assert context.get_state("test") == "value"

    print("  [OK] Context builder works")

    return True


def test_executor_creation():
    """Test executor creation."""
    print("\n[TEST] Executor Creation")

    registry = SkillRegistry()
    registry.discover_skills()

    context = ContextBuilder().build()
    executor = SkillExecutor(registry, context)

    print(f"  Registry skills: {len(executor.registry)}")
    print(f"  Context DPI: {executor.context.dpi_ratio}")

    assert len(executor.registry) > 0
    print("  [OK] Executor created successfully")

    return True


def test_skill_categories():
    """Test skills are properly categorized."""
    print("\n[TEST] Skill Categories")

    registry = SkillRegistry()
    registry.discover_skills()

    for category in SkillCategory:
        count = registry.count(category=category)
        skills = registry.list_skills(category=category)
        print(f"  {category.value}: {count} skills")
        print(f"    {', '.join(skills[:3])}{'...' if count > 3 else ''}")

    return True


def test_skill_info():
    """Test skill info retrieval."""
    print("\n[TEST] Skill Info")

    registry = SkillRegistry()
    registry.discover_skills()

    context = ContextBuilder().build()
    executor = SkillExecutor(registry, context)

    info = executor.get_skill_info("radio_selection")
    print(f"  Name: {info['name']}")
    print(f"  Display: {info['display_name']}")
    print(f"  Category: {info['category']}")
    print(f"  Priority: {info['priority']}")

    assert info is not None
    assert info['name'] == "radio_selection"

    print("  [OK] Skill info retrieved")

    return True


def test_result_creation():
    """Test SkillResult creation."""
    print("\n[TEST] SkillResult Creation")

    # Success result
    success = SkillResult.success_result(
        data={"test": "value"},
        execution_time=0.5
    )
    print(f"  Success: {success.success}, Data: {success.data}")
    assert success.success
    assert success.data == {"test": "value"}

    # Failure result
    failure = SkillResult.failure_result(
        error="Test error",
        skill_name="test_skill"
    )
    print(f"  Failure: {failure.success}, Error: {failure.error}")
    assert not failure.success
    assert failure.error == "Test error"

    print("  [OK] Result creation works")

    return True


def test_context_clone():
    """Test context cloning."""
    print("\n[TEST] Context Clone")

    context = ContextBuilder().with_dpi_ratio(1.5).build()
    context.set_state("key", "value")

    cloned = context.clone()

    print(f"  Original DPI: {context.dpi_ratio}")
    print(f"  Cloned DPI: {cloned.dpi_ratio}")
    print(f"  Cloned state: {cloned.get_state('key')}")

    assert cloned.dpi_ratio == context.dpi_ratio
    assert cloned.get_state("key") == "value"

    # Verify independence
    cloned.set_state("key2", "value2")
    assert context.get_state("key2") is None

    print("  [OK] Context clone works")

    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("  Skills System Unit Tests")
    print("=" * 60)

    tests = [
        test_registry_discovery,
        test_skill_metadata,
        test_skill_can_handle,
        test_skill_validation,
        test_context_builder,
        test_executor_creation,
        test_skill_categories,
        test_skill_info,
        test_result_creation,
        test_context_clone,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"  [FAIL] FAILED: {e}")

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    if sys.stdout.encoding.lower() != 'utf-8':
        print("Note: Some Unicode characters may not display correctly")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
