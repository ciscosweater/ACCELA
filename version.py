"""
Version management for Bifrost.
This module provides version information for the application.
"""

__version__ = "1.1.1"
__version_info__ = (1, 1, 1)
__author__ = "Bifrost Team"
__email__ = ""
__description__ = "A PyQt6 GUI application for downloading Steam depots with advanced management features"

# Version constants for release management
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 1

# Development status: 'alpha', 'beta', 'rc', or 'stable'
STATUS = 'stable'

# Build number (optional, for CI/CD)
BUILD = None


def get_version_string():
    """
    Get the full version string.
    Returns:
        str: Version in format 'MAJOR.MINOR.PATCH' or 'MAJOR.MINOR.PATCH-STATUS' if status is not 'stable'
    """
    version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
    if STATUS != 'stable':
        version += f"-{STATUS}"
    return version


def get_version_info():
    """
    Get version information as a dictionary.
    Returns:
        dict: Dictionary containing version details
    """
    return {
        'version': __version__,
        'version_info': __version_info__,
        'major': VERSION_MAJOR,
        'minor': VERSION_MINOR,
        'patch': VERSION_PATCH,
        'status': STATUS,
        'build': BUILD,
        'author': __author__,
        'description': __description__
    }
