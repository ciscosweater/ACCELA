"""
Steam Schema utilities for ACCELA
"""
import os
from pathlib import Path
from utils.settings import get_settings

def is_steam_schema_enabled():
    """Check if Steam schema generation is enabled"""
    settings = get_settings()
    return settings.value("steam_schema_enabled", True, type=bool)

def should_auto_setup_credentials():
    """Check if auto-setup of Steam credentials is enabled"""
    settings = get_settings()
    return settings.value("auto_setup_steam_credentials", False, type=bool)

def set_steam_schema_setting(key, value):
    """Set a Steam schema setting"""
    settings = get_settings()
    settings.setValue(f"steam_schema_{key}", value)

def get_steam_schema_setting(key, default=None):
    """Get a Steam schema setting"""
    settings = get_settings()
    return settings.value(f"steam_schema_{key}", default)