#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skills System Demo

This script demonstrates how to use the Skills system for survey automation.
"""

import sys
import argparse
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


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_result(result: SkillResult):
    """Print skill execution result."""
    status = "[OK] SUCCESS" if result.success else "✗ FAILED"
    print(f"  {status}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Skill: {result.skill_name}")

    if result.success and result.data:
        print(f"  Data: {result.data}")
    elif not result.success and result.error:
        print(f"  Error: {result.error}")


def demo_list_skills(registry: SkillRegistry):
    """Demonstrate listing all available skills."""
    print_section("Available Skills")

    for category in SkillCategory:
        skills = registry.list_skills(category=category)
        if skills:
            print(f"\n{category.value.upper()}:")
            for skill_name in skills:
                try:
                    metadata = registry.get_metadata(skill_name)
                    print(f"  - {metadata.display_name} ({metadata.name})")
                    print(f"    v{metadata.version} | {metadata.description}")
                except Exception as e:
                    print(f"  - {skill_name} (Error: {e})")


def demo_browser_setup(executor: SkillExecutor):
    """Demonstrate browser setup."""
    print_section("Browser Setup Demo")

    # Setup browser for analysis (headless)
    result = executor.execute_skill(
        "browser_setup_for_analysis",
        {
            "headless": True,
            "channel": "auto"
        }
    )

    print_result(result)

    if result.success:
        # Store browser resources in context
        data = result.data
        executor.context.playwright_instance = data["playwright_instance"]
        executor.context.browser = data["browser"]
        executor.context.browser_context = data["context"]
        executor.context.page = data["page"]

        print("\n  Browser resources stored in context")

    return result.success


def demo_question_detection(executor: SkillExecutor, url: str):
    """Demonstrate question detection on a survey."""
    print_section("Question Detection Demo")

    if not executor.context.has_page():
        print("  Error: No browser context available")
        return False

    try:
        # Navigate to survey
        print("\n  Navigating to survey...")
        goto_result = executor.execute_skill(
            "goto_survey",
            {
                "url": url,
                "wait_until": "domcontentloaded"
            }
        )

        if not goto_result.success:
            print(f"  Failed to navigate: {goto_result.error}")
            return False

        print(f"  [OK] Navigated to: {goto_result.data['title']}")

        # Analyze survey
        print("\n  Analyzing survey structure...")
        analyze_result = executor.execute_skill(
            "survey_analysis",
            {}
        )

        if not analyze_result.success:
            print(f"  Failed to analyze: {analyze_result.error}")
            return False

        questions = analyze_result.data["questions"]
        print(f"  [OK] Found {len(questions)} questions")

        # Detect question types
        print("\n  Question details:")
        for q in questions[:5]:  # Show first 5
            print(f"    {q['topic']}: {q['type']}")
            if 'options' in q:
                print(f"      Options: {q['option_count']}")

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def demo_question_filling(executor: SkillExecutor):
    """Demonstrate question type skills."""
    print_section("Question Filling Demo")

    if not executor.context.has_page():
        print("  Error: No browser context available")
        return

    # Demo radio selection
    print("\n  Radio Selection:")
    result = executor.execute_skill(
        "radio_selection",
        {
            "page": executor.context.page,
            "probabilities": [1, 2, 3],
            "question_index": 1
        }
    )
    print_result(result)

    # Demo multiple selection
    print("\n  Multiple Selection:")
    result = executor.execute_skill(
        "multiple_selection",
        {
            "page": executor.context.page,
            "probabilities": [80, 60, 40],
            "question_index": 2
        }
    )
    print_result(result)

    # Demo blank filling
    print("\n  Blank Filling:")
    result = executor.execute_skill(
        "blank_filling",
        {
            "page": executor.context.page,
            "text_list": ["选项A", "选项B", "选项C"],
            "probabilities_list": [2, 3, 1],
            "question_index": 3
        }
    )
    print_result(result)


def demo_verification(executor: SkillExecutor):
    """Demonstrate verification handling."""
    print_section("Verification Demo")

    print("  Note: Verification skills require actual verification elements")
    print("  This is a demonstration of the API")

    # Intelligent verification
    print("\n  Intelligent Verification (API demo):")
    print("    - Input: locator, dpi_ratio")
    print("    - Output: click_position, screen coordinates")

    # Slider verification
    print("\n  Slider Verification (API demo):")
    print("    - Input: locator, dpi_ratio")
    print("    - Output: drag positions, distance")


def demo_cleanup(executor: SkillExecutor):
    """Demonstrate browser cleanup."""
    print_section("Browser Cleanup Demo")

    result = executor.execute_skill(
        "browser_cleanup",
        {
            "page": executor.context.page,
            "context": executor.context.browser_context,
            "browser": executor.context.browser,
            "playwright_instance": executor.context.playwright_instance,
        }
    )

    print_result(result)

    if result.success:
        # Clear context references
        executor.context.page = None
        executor.context.browser_context = None
        executor.context.browser = None
        executor.context.playwright_instance = None


def demo_skill_matching(executor: SkillExecutor):
    """Demonstrate automatic skill matching."""
    print_section("Skill Matching Demo")

    test_tasks = [
        {"probabilities": [1, 2, 3], "question_index": 1},
        {"info_list": [["A", "B"], [1, 1]], "question_index": 1},
        {"probabilities_list": [[1, 2], [2, 1]], "question_index": 1},
        {"verification_type": "intelligent"},
        {"task_type": "browser_setup", "headless": True},
    ]

    for task in test_tasks:
        print(f"\n  Task: {task}")
        result = executor.execute_best_skill(task)
        if result.success:
            print(f"    [OK] Matched: {result.skill_name}")
        else:
            print(f"    ✗ No match or error: {result.error}")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Skills System Demo")
    parser.add_argument("--url", help="Survey URL for live demo")
    parser.add_argument("--no-browser", action="store_true", help="Skip browser demo")
    parser.add_argument("--list", action="store_true", help="List available skills and exit")

    args = parser.parse_args()

    # Create registry and discover skills
    print_section("Skills System Demo")
    print("  Initializing registry and discovering skills...")

    registry = SkillRegistry()
    registry.discover_skills()

    print(f"  [OK] Discovered {registry.count()} skills")

    # List skills if requested
    if args.list:
        demo_list_skills(registry)
        return

    # Create context and executor
    context = ContextBuilder().build()
    executor = SkillExecutor(registry, context)

    # Show available skills
    demo_list_skills(registry)

    # Demonstrate skill matching
    demo_skill_matching(executor)

    # Browser demos
    if not args.no_browser:
        browser_ok = demo_browser_setup(executor)

        if browser_ok and args.url:
            demo_question_detection(executor, args.url)
            demo_question_filling(executor)

        if browser_ok:
            demo_cleanup(executor)

    print_section("Demo Complete")
    print("  The Skills system provides a modular, extensible framework")
    print("  for survey automation tasks.")


if __name__ == "__main__":
    main()
