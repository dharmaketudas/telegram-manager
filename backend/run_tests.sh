#!/bin/bash

# Telegram Contact Manager - Test Runner Script
# Runs unit and integration tests for the backend

set -e  # Exit on error

echo "🧪 Running Telegram Contact Manager Backend Tests"
echo "=================================================="

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Must be run from the backend directory"
    echo "   Run: cd telegram-manager/backend && ./run_tests.sh"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Warning: Virtual environment not found"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "❌ Error: pytest not installed"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

case "$TEST_TYPE" in
    unit)
        echo ""
        echo "▶️  Running Unit Tests..."
        pytest tests/unit/ -v $VERBOSE
        ;;
    integration)
        echo ""
        echo "▶️  Running Integration Tests..."
        pytest tests/integration/ -v $VERBOSE
        ;;
    coverage)
        echo ""
        echo "▶️  Running Tests with Coverage..."
        pytest --cov=src --cov-report=html --cov-report=term-missing
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    quick)
        echo ""
        echo "▶️  Running Quick Tests (no markers)..."
        pytest tests/unit/ -v --tb=line
        ;;
    all)
        echo ""
        echo "▶️  Running All Tests..."
        pytest -v $VERBOSE
        ;;
    *)
        echo "❌ Unknown test type: $TEST_TYPE"
        echo ""
        echo "Usage: ./run_tests.sh [test_type] [verbose_flag]"
        echo ""
        echo "Test types:"
        echo "  all         - Run all tests (default)"
        echo "  unit        - Run only unit tests"
        echo "  integration - Run only integration tests"
        echo "  coverage    - Run tests with coverage report"
        echo "  quick       - Run quick tests with minimal output"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh coverage"
        echo "  ./run_tests.sh all -vv"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
