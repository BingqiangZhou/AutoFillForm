"""
Skill context management.
Provides shared context for skill execution.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Callable
from playwright.sync_api import Browser, BrowserContext, Page


@dataclass
class SkillContext:
    """
    Shared context for skill execution.

    Provides access to browser instances, configuration, logging,
    and state management for all skills.
    """

    # Browser resources
    page: Optional[Page] = None
    browser: Optional[Browser] = None
    browser_context: Optional[BrowserContext] = None
    playwright_instance: Any = None

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Logging
    logger: Optional[Any] = None
    log_callback: Optional[Callable[[str], None]] = None

    # State management
    state: Dict[str, Any] = field(default_factory=dict)

    # Display settings
    dpi_ratio: float = 1.0

    # Execution metadata
    current_url: Optional[str] = None
    current_task: Optional[str] = None

    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message through the available logger.

        Args:
            message: Message to log
            level: Log level (debug, info, warning, error)
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message)
        elif self.log_callback:
            self.log_callback(message)

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the state.

        Args:
            key: State key
            default: Default value if key doesn't exist

        Returns:
            The state value or default
        """
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the state.

        Args:
            key: State key
            value: Value to set
        """
        self.state[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)

    def has_browser(self) -> bool:
        """Check if browser resources are available."""
        return self.browser is not None and self.page is not None

    def has_page(self) -> bool:
        """Check if page is available."""
        return self.page is not None

    def cleanup_browser(self) -> None:
        """
        Clean up browser resources.

        Safely closes page, context, browser, and playwright instance.
        """
        if self.page:
            try:
                self.page.close()
            except Exception:
                pass
            self.page = None

        if self.browser_context:
            try:
                self.browser_context.close()
            except Exception:
                pass
            self.browser_context = None

        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
            self.browser = None

        if self.playwright_instance:
            try:
                self.playwright_instance.stop()
            except Exception:
                pass
            self.playwright_instance = None

    def clone(self) -> "SkillContext":
        """
        Create a shallow copy of the context.

        Returns:
            A new SkillContext with copied values
        """
        return SkillContext(
            page=self.page,
            browser=self.browser,
            browser_context=self.browser_context,
            playwright_instance=self.playwright_instance,
            config=self.config.copy(),
            logger=self.logger,
            log_callback=self.log_callback,
            state=self.state.copy(),
            dpi_ratio=self.dpi_ratio,
            current_url=self.current_url,
            current_task=self.current_task,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary (excluding non-serializable objects).

        Returns:
            Dictionary representation of the context
        """
        return {
            "config": self.config,
            "state": self.state,
            "dpi_ratio": self.dpi_ratio,
            "current_url": self.current_url,
            "current_task": self.current_task,
            "has_browser": self.has_browser(),
            "has_page": self.has_page(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillContext":
        """
        Create context from dictionary.

        Args:
            data: Dictionary containing context data

        Returns:
            A new SkillContext instance
        """
        return cls(
            config=data.get("config", {}),
            state=data.get("state", {}),
            dpi_ratio=data.get("dpi_ratio", 1.0),
            current_url=data.get("current_url"),
            current_task=data.get("current_task"),
        )


class ContextBuilder:
    """
    Builder for creating SkillContext instances with a fluent interface.
    """

    def __init__(self):
        """Initialize the builder."""
        self._page = None
        self._browser = None
        self._browser_context = None
        self._playwright_instance = None
        self._config = {}
        self._logger = None
        self._log_callback = None
        self._state = {}
        self._dpi_ratio = 1.0
        self._current_url = None
        self._current_task = None

    def with_browser(
        self,
        playwright_instance: Any = None,
        browser: Browser = None,
        context: BrowserContext = None,
        page: Page = None
    ) -> "ContextBuilder":
        """Set browser resources."""
        self._playwright_instance = playwright_instance
        self._browser = browser
        self._browser_context = context
        self._page = page
        return self

    def with_config(self, config: Dict[str, Any]) -> "ContextBuilder":
        """Set configuration."""
        self._config = config
        return self

    def with_logger(self, logger: Any, callback: Optional[Callable[[str], None]] = None) -> "ContextBuilder":
        """Set logger."""
        self._logger = logger
        self._log_callback = callback
        return self

    def with_state(self, state: Dict[str, Any]) -> "ContextBuilder":
        """Set initial state."""
        self._state = state
        return self

    def with_dpi_ratio(self, ratio: float) -> "ContextBuilder":
        """Set DPI ratio."""
        self._dpi_ratio = ratio
        return self

    def with_url(self, url: str) -> "ContextBuilder":
        """Set current URL."""
        self._current_url = url
        return self

    def with_task(self, task: str) -> "ContextBuilder":
        """Set current task."""
        self._current_task = task
        return self

    def build(self) -> SkillContext:
        """Build and return the SkillContext."""
        return SkillContext(
            page=self._page,
            browser=self._browser,
            browser_context=self._browser_context,
            playwright_instance=self._playwright_instance,
            config=self._config,
            logger=self._logger,
            log_callback=self._log_callback,
            state=self._state,
            dpi_ratio=self._dpi_ratio,
            current_url=self._current_url,
            current_task=self._current_task,
        )


class ContextManager:
    """
    Manager for context lifecycle and cleanup.
    """

    def __init__(self):
        """Initialize the context manager."""
        self._contexts: Dict[str, SkillContext] = {}
        self._default_context: Optional[SkillContext] = None

    def create_context(self, name: str, context: SkillContext) -> SkillContext:
        """
        Create and register a named context.

        Args:
            name: Context name
            context: The context to register

        Returns:
            The registered context
        """
        self._contexts[name] = context
        return context

    def get_context(self, name: str) -> Optional[SkillContext]:
        """
        Get a named context.

        Args:
            name: Context name

        Returns:
            The context or None if not found
        """
        return self._contexts.get(name)

    def set_default(self, context: SkillContext) -> None:
        """
        Set the default context.

        Args:
            context: The context to set as default
        """
        self._default_context = context

    def get_default(self) -> Optional[SkillContext]:
        """Get the default context."""
        return self._default_context

    def remove_context(self, name: str) -> bool:
        """
        Remove a named context.

        Args:
            name: Context name

        Returns:
            True if context was removed
        """
        if name in self._contexts:
            del self._contexts[name]
            return True
        return False

    def cleanup_all(self) -> None:
        """Clean up all registered contexts."""
        for context in self._contexts.values():
            context.cleanup_browser()
        if self._default_context:
            self._default_context.cleanup_browser()
        self._contexts.clear()

    def cleanup_context(self, name: str) -> bool:
        """
        Clean up a specific context.

        Args:
            name: Context name

        Returns:
            True if context was cleaned up
        """
        context = self._contexts.get(name)
        if context:
            context.cleanup_browser()
            del self._contexts[name]
            return True
        return False

    def list_contexts(self) -> list[str]:
        """List all registered context names."""
        return list(self._contexts.keys())
