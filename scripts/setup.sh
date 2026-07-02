#!/bin/bash
# ====================================================================
# AI HUMANIZER - SETUP SCRIPT
# ====================================================================
# Complete setup script for AI Humanizer project
# Runs on Linux, macOS, and Windows (WSL/Git Bash)
# ====================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${BLUE}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_header() {
    echo ""
    echo "============================================================"
    echo -e "${BLUE}$1${NC}"
    echo "============================================================"
}

# ====================================================================
# CHECK PREREQUISITES
# ====================================================================

check_prerequisites() {
    print_header "🔍 CHECKING PREREQUISITES"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python: $PYTHON_VERSION"
    else
        print_error "Python 3.9+ is required. Please install Python."
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip: Installed"
    else
        print_error "pip is required. Please install pip."
        exit 1
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git: $GIT_VERSION"
    else
        print_warning "Git not found. Install Git for version control."
    fi
    
    echo ""
}

# ====================================================================
# SETUP VIRTUAL ENVIRONMENT
# ====================================================================

setup_venv() {
    print_header "📦 SETTING UP VIRTUAL ENVIRONMENT"
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Remove and recreate? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            print_message "Removed existing venv"
        else
            print_message "Using existing venv"
            return 0
        fi
    fi
    
    print_message "Creating virtual environment..."
    python3 -m venv venv
    
    if [ -d "venv" ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    echo ""
}

# ====================================================================
# ACTIVATE VIRTUAL ENVIRONMENT
# ====================================================================

activate_venv() {
    print_header "🔄 ACTIVATING VIRTUAL ENVIRONMENT"
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "Virtual environment activated (Windows)"
    else
        print_warning "Could not activate venv automatically"
        print_message "Please activate manually:"
        echo "  Linux/macOS: source venv/bin/activate"
        echo "  Windows:     venv\\Scripts\\activate"
    fi
    
    echo ""
}

# ====================================================================
# INSTALL DEPENDENCIES
# ====================================================================

install_dependencies() {
    print_header "📥 INSTALLING DEPENDENCIES"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_message "Installing from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
    
    echo ""
}

# ====================================================================
# DOWNLOAD NLP MODELS
# ====================================================================

download_nlp_models() {
    print_header "🧠 DOWNLOADING NLP MODELS"
    
    # Download spaCy model
    print_message "Downloading spaCy model..."
    python -m spacy download en_core_web_sm
    
    if [ $? -eq 0 ]; then
        print_success "spaCy model downloaded"
    else
        print_warning "spaCy model download failed"
    fi
    
    # Download NLTK data
    print_message "Downloading NLTK data..."
    python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt'); nltk.download('punkt_tab')"
    
    if [ $? -eq 0 ]; then
        print_success "NLTK data downloaded"
    else
        print_warning "NLTK data download failed"
    fi
    
    echo ""
}

# ====================================================================
# CREATE DIRECTORIES
# ====================================================================

create_directories() {
    print_header "📁 CREATING DIRECTORIES"
    
    directories=(
        "logs"
        "uploads"
        "backend/word_data"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created: $dir"
        else
            print_message "Already exists: $dir"
        fi
    done
    
    echo ""
}

# ====================================================================
# SETUP ENVIRONMENT FILE
# ====================================================================

setup_env_file() {
    print_header "📝 SETTING UP ENVIRONMENT FILE"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env from .env.example"
            print_warning "Please edit .env and add your API keys"
        else
            print_warning ".env.example not found"
        fi
    else
        print_message ".env already exists"
    fi
    
    echo ""
}

# ====================================================================
# SHOW COMPLETION
# ====================================================================

show_completion() {
    print_header "🎉 SETUP COMPLETE!"
    
    echo "✅ AI Humanizer is ready to use!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Activate virtual environment:"
    echo "     source venv/bin/activate  (Linux/macOS)"
    echo "     venv\\Scripts\\activate     (Windows)"
    echo "  3. Run the API:"
    echo "     python -m backend.main"
    echo "  4. Open browser:"
    echo "     http://localhost:8000/docs"
    echo ""
    echo "📚 Useful commands:"
    echo "  - Run tests:      pytest tests/ -v"
    echo "  - Download word data: python scripts/download_word_data.py"
    echo "  - Deactivate venv: deactivate"
    echo ""
    echo "============================================================"
}

# ====================================================================
# MAIN FUNCTION
# ====================================================================

main() {
    print_header "🚀 AI HUMANIZER SETUP"
    echo "This script will set up the entire AI Humanizer project."
    echo ""
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$PYTHON_VERSION < 3.9" | bc -l) )); then
        print_error "Python 3.9+ required. Found version: $PYTHON_VERSION"
        exit 1
    fi
    
    # Run setup steps
    check_prerequisites
    setup_venv
    activate_venv
    install_dependencies
    download_nlp_models
    create_directories
    setup_env_file
    show_completion
}

# ====================================================================
# RUN SCRIPT
# ====================================================================

# Check if running on Windows (Git Bash)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "⚠️ Running on Windows with Git Bash"
    echo "   Some features may not work as expected."
    echo "   For best results, use WSL or Linux/macOS."
    echo ""
fi

# Run main
main

# ====================================================================
# END OF FILE
# ====================================================================