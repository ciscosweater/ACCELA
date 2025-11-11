"""
Exemplo de como adicionar um novo tema ao sistema

Para adicionar um novo tema, siga estes 3 passos simples:

1. Crie uma classe de cores herdando de BaseColors
2. Crie uma classe de tema herdando de BaseTheme  
3. Registre o tema no THEME_REGISTRY
"""

# Exemplo: Tema "Dark Purple"
from ui.theme import BaseColors, BaseTheme, THEME_REGISTRY, register_theme


class DarkPurpleColors(BaseColors):
    """Dark Purple theme colors"""
    THEME_NAME = "Dark Purple"
    
    # Override primary colors with purple palette
    PRIMARY = "#9b59b6"           
    PRIMARY_LIGHT = "#a569bd"     
    PRIMARY_DARK = "#8e44ad"      
    PRIMARY_VARIANT = "#9b59b6"   
    
    # Override neutral colors with darker palette
    BACKGROUND = "#0a0a0a"        
    SURFACE = "#1a1a1a"           
    SURFACE_LIGHT = "#2a2a2a"     
    SURFACE_DARK = "#050505"      
    
    # Override border colors
    BORDER = "#2a2a2a"            
    BORDER_LIGHT = "#3a3a3a"      
    BORDER_DARK = "#1a1a1a"       
    
    # Override text colors
    TEXT_PRIMARY = "#e0e0e0"      
    TEXT_SECONDARY = "#b0b0b0"     
    TEXT_DISABLED = "#606060"      
    TEXT_ACCENT = "#9b59b6"       


class DarkPurpleTheme(BaseTheme):
    """Dark Purple theme"""
    
    def __init__(self):
        super().__init__(DarkPurpleColors)


# Registrar o tema no sistema
register_theme("Dark Purple", DarkPurpleTheme)


# Exemplo: Tema "Ocean Blue"
class OceanBlueColors(BaseColors):
    """Ocean Blue theme colors"""
    THEME_NAME = "Ocean Blue"
    
    # Override primary colors with ocean palette
    PRIMARY = "#3498db"           
    PRIMARY_LIGHT = "#5dade2"     
    PRIMARY_DARK = "#2980b9"      
    PRIMARY_VARIANT = "#3498db"   
    
    # Override neutral colors with ocean palette
    BACKGROUND = "#0f1419"        
    SURFACE = "#1a2332"           
    SURFACE_LIGHT = "#243447"     
    SURFACE_DARK = "#0a0e14"      
    
    # Override border colors
    BORDER = "#2c3e50"            
    BORDER_LIGHT = "#34495e"      
    BORDER_DARK = "#1c2833"       
    
    # Override text colors
    TEXT_PRIMARY = "#ecf0f1"      
    TEXT_SECONDARY = "#bdc3c7"     
    TEXT_DISABLED = "#7f8c8d"      
    TEXT_ACCENT = "#3498db"       


class OceanBlueTheme(BaseTheme):
    """Ocean Blue theme"""
    
    def __init__(self):
        super().__init__(OceanBlueColors)


# Registrar o tema no sistema
register_theme("Ocean Blue", OceanBlueTheme)


# Exemplo: Tema "Forest Green"
class ForestGreenColors(BaseColors):
    """Forest Green theme colors"""
    THEME_NAME = "Forest Green"
    
    # Override primary colors with forest palette
    PRIMARY = "#27ae60"           
    PRIMARY_LIGHT = "#2ecc71"     
    PRIMARY_DARK = "#229954"      
    PRIMARY_VARIANT = "#27ae60"   
    
    # Override neutral colors with forest palette
    BACKGROUND = "#0d1f0d"        
    SURFACE = "#1a2e1a"           
    SURFACE_LIGHT = "#243d24"     
    SURFACE_DARK = "#091409"      
    
    # Override border colors
    BORDER = "#1e3a1e"            
    BORDER_LIGHT = "#2a4a2a"      
    BORDER_DARK = "#142a14"       
    
    # Override text colors
    TEXT_PRIMARY = "#d5e8d4"      
    TEXT_SECONDARY = "#a8c4a7"     
    TEXT_DISABLED = "#6b8e6a"      
    TEXT_ACCENT = "#27ae60"       


class ForestGreenTheme(BaseTheme):
    """Forest Green theme"""
    
    def __init__(self):
        super().__init__(ForestGreenColors)


# Registrar o tema no sistema
register_theme("Forest Green", ForestGreenTheme)