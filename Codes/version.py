"""
AutoFillForm - Version Information

Centralized version management for the application.
"""

__version__ = "5.0.0"
__title__ = "AutoFillForm"
__fullname__ = f"{__title__} {__version__}"

# For QSettings compatibility (preserves user settings)
__legacy_version__ = f"V{__version__.split('.')[0]}"

__all__ = ['__version__', '__title__', '__fullname__', '__legacy_version__']
