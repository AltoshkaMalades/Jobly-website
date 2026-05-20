# test.ps1 - Test runner script for Django Job Aggregator
# Run all tests with coverage and cleanup

param(
    [string]$TestType = "all",
    [switch]$NoCoverage,
    [switch]$CleanOnly,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host "Django Job Aggregator Test Runner" -ForegroundColor Cyan
    Write-Host "Usage: .\test.ps1 [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -TestType <type>    Test type: all, unit, integration, fast (default: all)"
    Write-Host "  -NoCoverage         Run tests without coverage report"
    Write-Host "  -CleanOnly          Only clean temporary files, don't run tests"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\test.ps1                          # Run all tests with coverage"
    Write-Host "  .\test.ps1 -TestType unit          # Run only unit tests"
    Write-Host "  .\test.ps1 -NoCoverage             # Run tests without coverage"
    Write-Host "  .\test.ps1 -CleanOnly              # Clean temporary files"
    Write-Host ""
    Write-Host "VS Code Shortcuts:" -ForegroundColor Magenta
    Write-Host "  Ctrl+Shift+B    - Run all tests with coverage"
    Write-Host "  Ctrl+Shift+P -> 'Tasks: Run Task' - See all test options"
    exit 0
}

# Function to clean temporary files
function Clean-TempFiles {
    Write-Host "?? Cleaning up temporary files..." -ForegroundColor Yellow

    # Remove Python cache files
    Get-ChildItem -Path . -Recurse -Include "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Include "*.pyc" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Include "*.pyo" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

    # Remove test artifacts
    Get-ChildItem -Path . -Recurse -Include ".pytest_cache" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Include "*.coverage" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Include "coverage.xml" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

    Write-Host "? Cleanup completed!" -ForegroundColor Green
}

# Clean only mode
if ($CleanOnly) {
    Clean-TempFiles
    exit 0
}

# Activate virtual environment
Write-Host "? Activating virtual environment..." -ForegroundColor Cyan
& ".\envir\Scripts\Activate.ps1"

# Build pytest command based on parameters
$pytestCmd = "python -m pytest"

switch ($TestType) {
    "unit" {
        $pytestCmd += " tests/unit/"
        Write-Host "? Running unit tests only..." -ForegroundColor Blue
    }
    "integration" {
        $pytestCmd += " tests/integration/"
        Write-Host "? Running integration tests only..." -ForegroundColor Blue
    }
    "fast" {
        $pytestCmd += " -x --tb=short"
        Write-Host "? Running tests fast (no coverage, stop on first failure)..." -ForegroundColor Blue
    }
    default {
        # All tests with coverage
        if (-not $NoCoverage) {
            $pytestCmd += " --cov=. --cov-report=html --cov-report=term-missing"
        }
        Write-Host "? Running all tests..." -ForegroundColor Blue
        if (-not $NoCoverage) {
            Write-Host "? Coverage report will be generated" -ForegroundColor Gray
        }
    }
}

# Add verbose output
$pytestCmd += " -v"

# Run the tests
Write-Host "Command: $pytestCmd" -ForegroundColor Gray

Invoke-Expression $pytestCmd
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "? Tests completed successfully!" -ForegroundColor Green
    if (-not $NoCoverage -and $TestType -eq "all") {
        Write-Host "? Coverage report saved to htmlcov/index.html" -ForegroundColor Cyan
        Write-Host "? Open coverage report in browser: htmlcov/index.html" -ForegroundColor Cyan
    }
} else {
    Write-Host "? Tests failed with exit code: $exitCode" -ForegroundColor Red
}

# Always clean up
Write-Host "" -ForegroundColor White
Clean-TempFiles

exit $exitCode