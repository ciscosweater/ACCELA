from PyQt6.QtCore import QSettings

# --- Constants for QSettings ---
APP_NAME = "ACCELA"
ORG_NAME = "ACCELA"

# --- Steam Schema Generator Settings ---
STEAM_SCHEMA_SETTINGS = {
    "enabled": {
        "default": True,
        "type": bool,
        "description": "Enable automatic Steam Schema generation after downloads"
    },
    "mode": {
        "default": "update",
        "type": str,
        "description": "Schema handling mode: 'overwrite', 'update', or 'skip'"
    },
    "auto_setup_credentials": {
        "default": False,
        "type": bool,
        "description": "Automatically prompt for Steam API credentials if not configured"
    }
}

# --- SLSsteam Integration Settings ---
# Note: Only slssteam_mode is currently implemented and functional

# --- Font Settings ---
FONT_SETTINGS = {
    "selected_font": {
        "default": "TrixieCyrG-Plain Regular",
        "type": str,
        "description": "Selected application font"
    }
}

# --- Theme Settings ---
THEME_SETTINGS = {
    "current_theme": {
        "default": "default_dark",
        "type": str,
        "description": "Currently selected theme name"
    },
    "custom_colors": {
        "default": {},
        "type": dict,
        "description": "Custom color overrides for current theme"
    },
    "custom_fonts": {
        "default": {},
        "type": dict,
        "description": "Custom font settings for current theme"
    },
    "auto_restart_on_theme_change": {
        "default": True,
        "type": bool,
        "description": "Automatically restart application when theme changes"
    }
}

# --- Available Themes ---
AVAILABLE_THEMES = {
    "default_dark": {
        "name": "Default Dark",
        "description": "Default ACCELA dark theme",
        "colors": {
            "primary": "#C06C84",
            "primary_light": "#D08C9C",
            "primary_dark": "#A05C74",
            "secondary": "#6C84C0",
            "secondary_light": "#8CA4D8",
            "secondary_dark": "#5C74B0",
            "success": "#6CC084",
            "warning": "#C0A06C",
            "error": "#C06C84",
            "background": "#1A1A1A",
            "surface": "#252525",
            "surface_light": "#303030",
            "surface_dark": "#151515",
            "border": "#353535",
            "border_light": "#454545",
            "border_dark": "#252525",
            "text_primary": "#E8E8E8",
            "text_secondary": "#B0B0B0",
            "text_disabled": "#606060",
            "text_on_primary": "#FFFFFF"
        },
        "fonts": {
            "primary": "TrixieCyrG-Plain Regular",
            "fallback": "Arial",
            "h1_size": 24,
            "h2_size": 18,
            "h3_size": 14,
            "body_size": 12,
            "caption_size": 10
        }
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "description": "Neon cyberpunk theme with bright accents",
        "colors": {
            "primary": "#FF00FF",
            "primary_light": "#FF33FF",
            "primary_dark": "#CC00CC",
            "secondary": "#00FFFF",
            "secondary_light": "#33FFFF",
            "secondary_dark": "#00CCCC",
            "success": "#00FF00",
            "warning": "#FFAA00",
            "error": "#FF0066",
            "background": "#0A0A0A",
            "surface": "#1A0A1A",
            "surface_light": "#2A1A2A",
            "surface_dark": "#050005",
            "border": "#FF00FF",
            "border_light": "#FF33FF",
            "border_dark": "#CC00CC",
            "text_primary": "#FFFFFF",
            "text_secondary": "#CCCCCC",
            "text_disabled": "#666666",
            "text_on_primary": "#000000"
        },
        "fonts": {
            "primary": "TrixieCyrG-Plain Regular",
            "fallback": "Arial",
            "h1_size": 26,
            "h2_size": 20,
            "h3_size": 16,
            "body_size": 13,
            "caption_size": 11
        }
    },
    "ocean": {
        "name": "Ocean",
        "description": "Calm ocean-inspired theme",
        "colors": {
            "primary": "#006994",
            "primary_light": "#0088BB",
            "primary_dark": "#004A66",
            "secondary": "#00A8CC",
            "secondary_light": "#33C8DD",
            "secondary_dark": "#0088AA",
            "success": "#00AA66",
            "warning": "#CC8800",
            "error": "#CC4466",
            "background": "#0A1419",
            "surface": "#1A2429",
            "surface_light": "#2A3439",
            "surface_dark": "#050A0F",
            "border": "#2A4455",
            "border_light": "#3A5566",
            "border_dark": "#1A3344",
            "text_primary": "#E8F4F8",
            "text_secondary": "#B8D4DC",
            "text_disabled": "#667788",
            "text_on_primary": "#FFFFFF"
        },
        "fonts": {
            "primary": "MotivaSansRegular",
            "fallback": "Arial",
            "h1_size": 24,
            "h2_size": 18,
            "h3_size": 14,
            "body_size": 12,
            "caption_size": 10
        }
    },
    "minimal": {
        "name": "Minimal",
        "description": "Clean minimal theme with grays",
        "colors": {
            "primary": "#666666",
            "primary_light": "#888888",
            "primary_dark": "#444444",
            "secondary": "#999999",
            "secondary_light": "#BBBBBB",
            "secondary_dark": "#777777",
            "success": "#66AA66",
            "warning": "#AAAA66",
            "error": "#AA6666",
            "background": "#FFFFFF",
            "surface": "#F5F5F5",
            "surface_light": "#FAFAFA",
            "surface_dark": "#EEEEEE",
            "border": "#DDDDDD",
            "border_light": "#E5E5E5",
            "border_dark": "#CCCCCC",
            "text_primary": "#333333",
            "text_secondary": "#666666",
            "text_disabled": "#999999",
            "text_on_primary": "#FFFFFF"
        },
        "fonts": {
            "primary": "Arial",
            "fallback": "Helvetica",
            "h1_size": 22,
            "h2_size": 16,
            "h3_size": 13,
            "body_size": 11,
            "caption_size": 9
        }
    },
    "bifrost_steam": {
        "name": "Bifrost Steam",
        "description": "Authentic Steam client Bifrost theme with dark blue interface",
        "colors": {
            "primary": "#66c0f4",
            "primary_light": "#7dd0f5",
            "primary_dark": "#4ba8e2",
            "secondary": "#1e90ff",
            "secondary_light": "#4ba0ff",
            "secondary_dark": "#0080dd",
            "success": "#4caf50",
            "success_light": "#66bb6a",
            "success_dark": "#388e3c",
            "warning": "#ff9800",
            "warning_light": "#ffb74d",
            "warning_dark": "#f57c00",
            "error": "#f44336",
            "error_light": "#ef5350",
            "error_dark": "#d32f2f",
            "background": "#171a21",
            "surface": "#1b2838",
            "surface_light": "#2a475e",
            "surface_dark": "#0e1419",
            "border": "#2a475e",
            "border_light": "#3c5d7a",
            "border_dark": "#1a2332",
            "text_primary": "#c7d5e0",
            "text_secondary": "#8b98a5",
            "text_disabled": "#4a5568",
            "text_on_primary": "#171a21"
        },
        "fonts": {
            "primary": "MotivaSansRegular",
            "fallback": "Arial",
            "h1_size": 24,
            "h2_size": 18,
            "h3_size": 14,
            "body_size": 13,
            "caption_size": 11
        }
    }
}

# --- Logging Settings ---
LOGGING_SETTINGS = {
    "simple_mode": {
        "default": True,
        "type": bool,
        "description": "Enable simplified log format (less verbose)"
    },
    "level": {
        "default": "WARNING",
        "type": str,
        "description": "Minimum log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    }
}

def get_settings():
    """
    Provides a global access point to the application's QSettings object.
    """
    return QSettings(ORG_NAME, APP_NAME)

def get_steam_schema_setting(key, default=None):
    """
    Get a Steam Schema Generator setting with proper type conversion.
    
    Args:
        key (str): Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value with proper type
    """
    settings = get_settings()
    setting_config = STEAM_SCHEMA_SETTINGS.get(key, {})
    
    if not setting_config:
        return default
    
    value = settings.value(f"steam_schema/{key}", setting_config["default"])
    
    # Type conversion
    if setting_config["type"] == bool:
        return bool(value)
    elif setting_config["type"] == int:
        return int(value) if value is not None else setting_config["default"]
    else:
        return value



def set_steam_schema_setting(key, value):
    """
    Set a Steam Schema Generator setting.
    
    Args:
        key (str): Setting key
        value: Setting value
    """
    settings = get_settings()
    settings.setValue(f"steam_schema/{key}", value)

def is_steam_schema_enabled():
    """Check if Steam Schema generation is enabled."""
    return get_steam_schema_setting("enabled", True)

def should_auto_setup_credentials():
    """Check if credentials should be auto-configured."""
    return get_steam_schema_setting("auto_setup_credentials", False)

def get_logging_setting(key, default=None):
    """
    Get a logging setting with proper type conversion.
    
    Args:
        key (str): Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value with proper type
    """
    settings = get_settings()
    setting_config = LOGGING_SETTINGS.get(key, {})
    
    if not setting_config:
        return default
    
    value = settings.value(f"logging/{key}", setting_config["default"])
    
    # Type conversion
    if setting_config["type"] == bool:
        return bool(value)
    elif setting_config["type"] == int:
        return int(value) if value is not None else setting_config["default"]
    else:
        return value

def get_font_setting(key, default=None):
    """
    Get a font setting with proper type conversion.
    
    Args:
        key (str): Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value with proper type
    """
    settings = get_settings()
    setting_config = FONT_SETTINGS.get(key, {})
    
    if not setting_config:
        return default
    
    value = settings.value(f"font/{key}", setting_config["default"])
    
    # Type conversion
    if setting_config["type"] == bool:
        return bool(value)
    elif setting_config["type"] == int:
        return int(value) if value is not None else setting_config["default"]
    else:
        return value

def set_font_setting(key, value):
    """
    Set a font setting.
    
    Args:
        key (str): Setting key
        value: Setting value
    """
    settings = get_settings()
    setting_config = FONT_SETTINGS.get(key, {})
    
    if setting_config:
        # Type validation
        if setting_config["type"] == bool and not isinstance(value, bool):
            value = bool(value)
        elif setting_config["type"] == int and not isinstance(value, int):
            value = int(value) if value is not None else setting_config["default"]
    
    settings.setValue(f"font/{key}", value)
    settings.sync()

def set_logging_setting(key, value):
    """
    Set a logging setting.
    
    Args:
        key (str): Setting key
        value: Setting value
    """
    settings = get_settings()
    setting_config = LOGGING_SETTINGS.get(key, {})
    
    if setting_config:
        # Type validation
        if setting_config["type"] == bool and not isinstance(value, bool):
            value = bool(value)
        elif setting_config["type"] == int and not isinstance(value, int):
            value = int(value) if value is not None else setting_config["default"]
    
    settings.setValue(f"logging/{key}", value)
    settings.sync()

def get_theme_setting(key, default=None):
    """
    Get a theme setting with proper type conversion.
    
    Args:
        key (str): Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value with proper type
    """
    settings = get_settings()
    setting_config = THEME_SETTINGS.get(key, {})
    
    if not setting_config:
        return default
    
    value = settings.value(f"theme/{key}", setting_config["default"])
    
    # Type conversion
    if setting_config["type"] == bool:
        return bool(value)
    elif setting_config["type"] == int:
        return int(value) if value is not None else setting_config["default"]
    elif setting_config["type"] == dict:
        return value if isinstance(value, dict) else setting_config["default"]
    else:
        return value

def set_theme_setting(key, value):
    """
    Set a theme setting.
    
    Args:
        key (str): Setting key
        value: Setting value
    """
    settings = get_settings()
    setting_config = THEME_SETTINGS.get(key, {})
    
    if setting_config:
        # Type validation
        if setting_config["type"] == bool and not isinstance(value, bool):
            value = bool(value)
        elif setting_config["type"] == int and not isinstance(value, int):
            value = int(value) if value is not None else setting_config["default"]
        elif setting_config["type"] == dict and not isinstance(value, dict):
            value = setting_config["default"]
    
    settings.setValue(f"theme/{key}", value)
    settings.sync()

def get_current_theme_config():
    """
    Get the complete configuration for the current theme.
    
    Returns:
        dict: Complete theme configuration with custom overrides applied
    """
    current_theme = get_theme_setting("current_theme", "default_dark")
    base_theme = AVAILABLE_THEMES.get(current_theme, AVAILABLE_THEMES["default_dark"])
    
    # Apply custom overrides
    custom_colors = get_theme_setting("custom_colors", {})
    custom_fonts = get_theme_setting("custom_fonts", {})
    
    theme_config = {
        "name": base_theme["name"],
        "description": base_theme["description"],
        "colors": {**base_theme["colors"], **custom_colors},
        "fonts": {**base_theme["fonts"], **custom_fonts}
    }
    
    return theme_config

def set_theme_colors(color_overrides):
    """
    Set custom color overrides for the current theme.
    
    Args:
        color_overrides (dict): Dictionary of color overrides
    """
    set_theme_setting("custom_colors", color_overrides)

def set_theme_fonts(font_overrides):
    """
    Set custom font overrides for the current theme.
    
    Args:
        font_overrides (dict): Dictionary of font overrides
    """
    set_theme_setting("custom_fonts", font_overrides)

def reset_theme_customizations():
    """Reset all custom theme overrides to defaults."""
    set_theme_setting("custom_colors", {})
    set_theme_setting("custom_fonts", {})

def get_available_themes():
    """
    Get list of available themes.
    
    Returns:
        list: List of theme dictionaries with id, name, and description
    """
    themes = []
    for theme_id, theme_config in AVAILABLE_THEMES.items():
        themes.append({
            "id": theme_id,
            "name": theme_config["name"],
            "description": theme_config["description"]
        })
    return themes

def apply_theme(theme_id):
    """
    Apply a theme by ID.
    
    Args:
        theme_id (str): ID of theme to apply
        
    Returns:
        bool: True if theme was applied successfully
    """
    if theme_id not in AVAILABLE_THEMES:
        return False
    
    # Reset customizations when switching themes
    reset_theme_customizations()
    set_theme_setting("current_theme", theme_id)
    return True

def should_auto_restart_on_theme_change():
    """Check if app should auto-restart when theme changes."""
    return get_theme_setting("auto_restart_on_theme_change", True)
