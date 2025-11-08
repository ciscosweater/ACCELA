#!/bin/bash

# ACCELA Unified Installation and Setup Script for Linux
# This script installs ACCELA to system directories and sets up the environment

set -euo pipefail  # Exit on error, undefined vars, and pipe failures
IFS=$'\n\t'       # Safer IFS

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Installation directories
readonly INSTALL_DIR="$HOME/.local/share/ACCELA/bin"
readonly DESKTOP_DIR="$HOME/.local/share/applications"
readonly ICONS_DIR="$HOME/.local/share/icons"
readonly USER_BIN="$HOME/.local/bin"

# Project directory (where this script is located)
readonly PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect Python command
detect_python() {
    local python_cmd=""
    
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    elif command -v python &> /dev/null; then
        local python_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
        if [[ $(echo "$python_version >= 3.8" | bc -l 2>/dev/null || echo "0") == "1" ]] || python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            python_cmd="python"
        else
            log_error "Python 3.8+ is required. Found: $python_version"
            exit 1
        fi
    else
        log_error "Python 3.8+ is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    echo "$python_cmd"
}

# Function to verify Python version
verify_python_version() {
    local python_cmd="$1"
    local python_version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local required_version="3.8"
    
    if ! $python_cmd -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_error "Python $required_version+ is required. Found: $python_version"
        exit 1
    fi
    
    log_success "Found Python: $($python_cmd --version)"
}

# Function to create virtual environment
create_virtual_env() {
    local python_cmd="$1"
    local venv_path="$2"
    
    if [[ ! -d "$venv_path" ]]; then
        log_info "Creating virtual environment..."
        $python_cmd -m venv "$venv_path"
        if [[ $? -eq 0 ]]; then
            log_success "Virtual environment created successfully"
        else
            log_error "Failed to create virtual environment"
            exit 1
        fi
    else
        log_warning "Virtual environment already exists"
        
        # Ask user if they want to recreate it
        read -p "Do you want to recreate the virtual environment? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing virtual environment..."
            rm -rf "$venv_path"
            log_info "Creating new virtual environment..."
            $python_cmd -m venv "$venv_path"
            log_success "Virtual environment recreated successfully"
        fi
    fi
}

# Function to activate virtual environment
activate_virtual_env() {
    local venv_path="$1"
    
    # Verify virtual environment was created
    if [[ ! -f "$venv_path/bin/activate" ]] && [[ ! -f "$venv_path/Scripts/activate" ]]; then
        log_error "Virtual environment activation script not found"
        exit 1
    fi
    
    # Activate virtual environment (cross-platform)
    if [[ -f "$venv_path/bin/activate" ]]; then
        # Linux/macOS
        source "$venv_path/bin/activate"
    elif [[ -f "$venv_path/Scripts/activate" ]]; then
        # Windows
        source "$venv_path/Scripts/activate"
    else
        log_error "Cannot find virtual environment activation script"
        exit 1
    fi
    
    log_success "Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    # Upgrade pip and setuptools
    log_info "Upgrading pip and setuptools..."
    pip install --upgrade pip setuptools wheel
    
    # Verify requirements.txt exists and is not empty
    if [[ ! -s "requirements.txt" ]]; then
        log_error "requirements.txt is empty or missing"
        exit 1
    fi
    
    # Install dependencies
    log_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    
    if [[ $? -eq 0 ]]; then
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies"
        exit 1
    fi
    
    # Verify critical packages are installed
    log_info "Verifying critical packages..."
    declare -A CRITICAL_PACKAGES=(
        ["PyQt6"]="PyQt6"
        ["steam"]="steam"
        ["requests"]="requests"
        ["beautifulsoup4"]="bs4"
    )
    
    for package_name in "${!CRITICAL_PACKAGES[@]}"; do
        import_name="${CRITICAL_PACKAGES[$package_name]}"
        if ! python -c "import $import_name" 2>/dev/null; then
            log_error "Critical package '$package_name' failed to install"
            exit 1
        fi
    done
    
    log_success "All critical packages verified"
    
    # Check if main.py can be imported (basic syntax check)
    log_info "Verifying main.py syntax..."
    if python -m py_compile main.py 2>/dev/null; then
        log_success "main.py syntax is valid"
    else
        log_warning "main.py has syntax issues, but dependencies are installed"
    fi
}

# Main installation function
main_install() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       ACCELA Installation Script       ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
    
    # Check if running from the correct directory
    if [ ! -f "$PROJECT_DIR/main.py" ] || [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        print_error "This script must be run from the ACCELA project directory containing main.py and requirements.txt"
        exit 1
    fi
    
    # Create installation directories
    print_status "Creating installation directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICONS_DIR"
    
    # Copy project files
    print_status "Copying ACCELA files to $INSTALL_DIR..."
    
    # Copy core Python files
    cp -r "$PROJECT_DIR"/*.py "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/core "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/ui "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/utils "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/assets "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/config "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/external "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/Steamless "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/SLSsteam-Any "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_DIR"/slscheevo_build "$INSTALL_DIR/" 2>/dev/null || true
    
    # Copy other important files
    cp "$PROJECT_DIR"/requirements.txt "$INSTALL_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR"/ACCELA "$INSTALL_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR"/accela.png "$INSTALL_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR"/icon.png "$INSTALL_DIR/" 2>/dev/null || true
    
    # Copy icon to system icons directory
    if [ -f "$PROJECT_DIR/icon.png" ]; then
        cp "$PROJECT_DIR/icon.png" "$ICONS_DIR/accela.png"
        print_status "Icon copied to $ICONS_DIR/accela.png"
    fi
    
    # Setup environment in installation directory
    cd "$INSTALL_DIR"
    
    # Detect and verify Python
    PYTHON_CMD=$(detect_python)
    verify_python_version "$PYTHON_CMD"
    
    # Create and setup virtual environment
    create_virtual_env "$PYTHON_CMD" ".venv"
    activate_virtual_env ".venv"
    install_dependencies
    
    # Create launcher script
    print_status "Creating launcher script..."
    cat > "$INSTALL_DIR/accela-launcher" << EOF
#!/bin/bash

# ACCELA Launcher Script
cd "\$(dirname "\$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run ACCELA
python main.py "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/accela-launcher"
    
    # Create .desktop file
    print_status "Creating desktop shortcut..."
    cat > "$DESKTOP_DIR/accela.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ACCELA
Comment=Steam Depot Downloader GUI
Exec=$INSTALL_DIR/accela-launcher %F
Icon=$ICONS_DIR/accela.png
Terminal=false
Categories=Game;Utility;
MimeType=application/zip;
StartupNotify=true
Keywords=steam;depot;downloader;games;
EOF
    
    chmod +x "$DESKTOP_DIR/accela.desktop"
    
    # Create symlink in user bin directory (optional)
    if [ -d "$USER_BIN" ] || mkdir -p "$USER_BIN" 2>/dev/null; then
        ln -sf "$INSTALL_DIR/accela-launcher" "$USER_BIN/accela" 2>/dev/null || true
        print_status "Created symlink: $USER_BIN/accela"
    fi
    
    # Set permissions
    print_status "Setting permissions..."
    chmod -R 755 "$INSTALL_DIR"
    find "$INSTALL_DIR" -name "*.py" -exec chmod 644 {} \;
    find "$INSTALL_DIR" -name "*.so" -exec chmod 755 {} \;
    find "$INSTALL_DIR" -name "*.exe" -exec chmod 755 {} \;
    
    # Return to original directory
    cd "$PROJECT_DIR"
}

# Function to setup environment only (no installation)
setup_only() {
    log_info "Setting up ACCELA environment..."
    
    # Check if running in the correct directory
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt not found. Please run this script from the ACCELA project directory."
        exit 1
    fi
    
    if [[ ! -f "main.py" ]]; then
        log_error "main.py not found. Please run this script from the ACCELA project directory."
        exit 1
    fi
    
    # Detect and verify Python
    PYTHON_CMD=$(detect_python)
    verify_python_version "$PYTHON_CMD"
    
    # Create and setup virtual environment
    create_virtual_env "$PYTHON_CMD" ".venv"
    activate_virtual_env ".venv"
    install_dependencies
    
    echo
    log_success "Environment setup complete!"
    echo
    echo -e "${BLUE}🎯 To run ACCELA:${NC}"
    echo -e "   ${YELLOW}source .venv/bin/activate && python main.py${NC}"
    echo
    if [[ -f "ACCELA" ]]; then
        echo -e "${BLUE}🎯 Or use the Linux executable:${NC}"
        echo -e "   ${YELLOW}./ACCELA${NC}"
        echo
    fi
    echo -e "${BLUE}🔧 To activate the environment manually:${NC}"
    echo -e "   ${YELLOW}source .venv/bin/activate${NC}"
    echo
    echo -e "${GREEN}🎉 ACCELA is ready to use!${NC}"
}

# Main script logic
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    ACCELA Setup & Installation Tool    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Check command line arguments
if [[ "${1:-}" == "--setup-only" ]]; then
    setup_only
else
    main_install
    
    print_status "Installation completed successfully!"
    echo
    echo -e "${GREEN}ACCELA has been installed to: $INSTALL_DIR${NC}"
    echo -e "${GREEN}Desktop shortcut created: $DESKTOP_DIR/accela.desktop${NC}"
    echo
    echo -e "${YELLOW}To run ACCELA:${NC}"
    echo -e "  • From applications menu: Look for 'ACCELA'"
    echo -e "  • From terminal: type 'accela' (if $USER_BIN is in PATH)"
    echo -e "  • Direct: $INSTALL_DIR/accela-launcher"
    echo
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}      Installation Complete!          ${NC}"
    echo -e "${BLUE}========================================${NC}"
fi