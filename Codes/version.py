"""
AutoFillForm - Version Information

Centralized version management for the application.
"""

__version__ = "5.0.1"
__title__ = "AutoFillForm"
__fullname__ = f"{__title__} {__version__}"

# Repository metadata
__repo_owner__ = "BingqiangZhou"
__repo_name__ = "AutoFillForm"
__repo_url__ = f"https://github.com/{__repo_owner__}/{__repo_name__}"

# For QSettings compatibility (preserves user settings)
__legacy_version__ = f"V{__version__.split('.')[0]}"

__all__ = [
    '__version__', '__title__', '__fullname__', '__legacy_version__',
    '__repo_owner__', '__repo_name__', '__repo_url__',
]
