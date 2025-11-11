# Sistema de Temas ACCELA

Sistema de temas escalável e simples para a aplicação ACCELA.

## Como Funciona

O sistema de temas foi projetado para ser extremamente simples de extender. Basta seguir 3 passos para adicionar um novo tema:

### 1. Criar Classe de Cores

Crie uma classe herdando de `BaseColors` e defina apenas as cores que deseja alterar:

```python
from ui.theme import BaseColors

class MeuTemaColors(BaseColors):
    THEME_NAME = "Meu Tema"
    
    # Altere apenas as cores que desejar
    PRIMARY = "#ff6b6b"           # Cor principal
    PRIMARY_LIGHT = "#ff8787"     # Hover
    PRIMARY_DARK = "#ff5252"      # Pressionado
    
    # Opcional: altere outras cores
    BACKGROUND = "#0a0a0a"
    SURFACE = "#1a1a1a"
```

### 2. Criar Classe do Tema

Crie uma classe herdando de `BaseTheme`:

```python
from ui.theme import BaseTheme

class MeuTemaTheme(BaseTheme):
    def __init__(self):
        super().__init__(MeuTemaColors)
```

### 3. Registrar o Tema

Registre o tema no sistema:

```python
from ui.theme import register_theme

register_theme("Meu Tema", MeuTemaTheme)
```

## Temas Disponíveis

- **ACCELA**: Tema padrão rosa/roxo
- **Bifrost**: Tema azul estilo Steam
- **Dark Purple**: Tema roxo escuro (exemplo)
- **Ocean Blue**: Tema azul oceano (exemplo)
- **Forest Green**: Tema verde floresta (exemplo)

## Uso na Aplicação

### Obter Tema Atual

```python
from ui.theme import get_current_theme

theme = get_current_theme()
theme.apply_theme_to_app(app)
```

### Obter Lista de Temas

```python
from ui.theme import get_available_themes

themes = get_available_themes()
# ['ACCELA', 'Bifrost', 'Dark Purple', 'Ocean Blue', 'Forest Green']
```

### Aplicar Tema Específico

```python
from ui.theme import THEME_REGISTRY

theme_class = THEME_REGISTRY["Bifrost"]
theme = theme_class()
theme.apply_theme_to_app(app)
```

### Salvar Tema Selecionado

```python
from PyQt6.QtCore import QSettings

settings = QSettings("ACCELA", "ACCELA")
settings.setValue("selected_theme", "Bifrost")
```

## Estrutura de Cores

### Cores Primárias
- `PRIMARY`: Cor principal do tema
- `PRIMARY_LIGHT`: Versão mais clara (hover)
- `PRIMARY_DARK`: Versão mais escura (pressed)
- `PRIMARY_VARIANT`: Variação alternativa

### Cores de Status
- `SUCCESS`: Verde para sucesso
- `WARNING`: Laranja para avisos
- `ERROR`: Vermelho para erros
- `SECONDARY`: Azul para informações

### Cores Neutras
- `BACKGROUND`: Fundo principal
- `SURFACE`: Fundo de cards/containers
- `SURFACE_LIGHT`: Hover de surfaces
- `SURFACE_DARK`: Surface mais escura

### Cores de Texto
- `TEXT_PRIMARY`: Texto principal
- `TEXT_SECONDARY`: Texto secundário
- `TEXT_DISABLED`: Texto desabilitado
- `TEXT_ON_PRIMARY`: Texto sobre fundo primário

### Cores de Borda
- `BORDER`: Borda padrão
- `BORDER_LIGHT`: Borda mais clara
- `BORDER_DARK`: Borda mais escura

## Componentes Estilizados

O sistema fornece estilos para componentes com as cores do tema:

```python
from ui.theme import ComponentStyles

# Botão primário
button_style = ComponentStyles.get_primary_button_style(theme.colors)

# Botão secundário  
button_style = ComponentStyles.get_secondary_button_style(theme.colors)

# Barra de progresso
progress_style = ComponentStyles.get_progress_bar_style(theme.colors)

# Card
card_style = ComponentStyles.get_card_style(theme.colors)

# Indicador de status
status_style = ComponentStyles.get_status_indicator_style('ready', theme.colors)
```

## Vantagens do Sistema

1. **Simples**: Apenas 3 passos para adicionar um tema
2. **Escalável**: Fácil adicionar infinitos temas
3. **Consistente**: Todos os temas seguem a mesma estrutura
4. **Flexível**: Altere apenas as cores que desejar
5. **Manutenível**: Código centralizado e organizado
6. **Compatível**: Mantém compatibilidade com código existente

## Boas Práticas

1. **Nomes Descritivos**: Use nomes claros para temas e cores
2. **Contraste**: Garanta bom contraste entre texto e fundo
3. **Consistência**: Mantenha paleta de cores coesa
4. **Teste**: Teste o tema em diferentes componentes
5. **Documentação**: Documente cores especiais ou significados

## Exemplo Completo

```python
# arquivo: ui/themes/my_custom_theme.py
from ui.theme import BaseColors, BaseTheme, register_theme

class MyCustomColors(BaseColors):
    THEME_NAME = "My Custom Theme"
    
    # Paleta roxa/neon
    PRIMARY = "#bf00ff"
    PRIMARY_LIGHT = "#cc33ff"
    PRIMARY_DARK = "#9900cc"
    
    # Fundo escuro com roxo
    BACKGROUND = "#0a0014"
    SURFACE = "#1a0028"
    SURFACE_LIGHT = "#2a0038"
    
    # Texto claro
    TEXT_PRIMARY = "#f0e6ff"
    TEXT_SECONDARY = "#ccb3ff"
    TEXT_ACCENT = "#bf00ff"

class MyCustomTheme(BaseTheme):
    def __init__(self):
        super().__init__(MyCustomColors)

# Registrar o tema
register_theme("My Custom Theme", MyCustomTheme)
```

Este sistema torna a adição de novos temas uma tarefa trivial e rápida, mantendo consistência e qualidade em toda a aplicação.