# Django Job Aggregator - Testing Guide

## 🧪 Running Tests

This project includes comprehensive test automation with multiple ways to run tests:

### **Method 1: VS Code Shortcuts (Recommended)**

#### **Ctrl+Shift+B** - Run All Tests with Coverage
- Automatically activates virtual environment
- Runs all tests with coverage reporting
- Generates HTML coverage report
- Cleans up temporary files
- **Default build task** - just press `Ctrl+Shift+B`!

#### **Ctrl+Shift+P → "Tasks: Run Task"** - Advanced Options
- **"Run All Tests with Coverage"** - Full test suite with coverage
- **"Run Unit Tests Only"** - Fast unit tests only
- **"Run Integration Tests Only"** - Integration tests only
- **"Run Tests Fast (No Coverage)"** - Quick tests without coverage
- **"Clean Temporary Files"** - Clean cache and artifacts
- **"Show Test Help"** - Display usage information

### **Method 2: PowerShell Script**

```powershell
# Run all tests with coverage
.\test.ps1

# Run only unit tests (fast)
.\test.ps1 -TestType unit

# Run tests without coverage
.\test.ps1 -NoCoverage

# Clean temporary files only
.\test.ps1 -CleanOnly

# Show help
.\test.ps1 -Help
```

### **Method 3: Direct pytest Commands**

```bash
# Activate environment first
.\envir\Scripts\Activate.ps1

# Run all tests with coverage
python -m pytest --cov=. --cov-report=html --cov-report=term-missing -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v
```

## 📊 Coverage Reports

After running tests with coverage, you'll get:
- **Terminal output**: Coverage percentages in terminal
- **HTML report**: Open `htmlcov/index.html` in your browser for detailed coverage

## 🧹 Automatic Cleanup

The test scripts automatically clean up:
- `__pycache__` directories
- `*.pyc` and `*.pyo` files
- `.pytest_cache` directories
- Coverage artifacts

## 📋 Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_models.py    # Model tests (24 tests)
│   └── test_accounts.py  # Account-specific tests
└── integration/          # Integration tests
    └── test_flows.py     # End-to-end test flows
```

## 🚀 Quick Start

1. **Open in VS Code**
2. **Press `Ctrl+Shift+B`** to run all tests
3. **Check coverage report** at `htmlcov/index.html`

That's it! Your tests will run automatically with coverage and cleanup. 🎉