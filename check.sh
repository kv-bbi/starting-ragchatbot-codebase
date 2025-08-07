#!/bin/bash

# Code Quality Checks Script
# Run code formatting and quality checks without making changes

set -e  # Exit on error

echo "🔍 Running code quality checks..."

echo "📝 Checking code formatting with Black..."
if uv run black --check .; then
    echo "✅ Code formatting is correct!"
else
    echo "❌ Code formatting issues found!"
    echo "💡 Run ./format.sh or 'uv run black .' to fix formatting"
    exit 1
fi

echo ""
echo "✅ All quality checks passed!"