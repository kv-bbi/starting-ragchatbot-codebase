#!/bin/bash

# Code Quality Tools Script
# Run code formatting and quality checks

set -e  # Exit on error

echo "🔧 Running code quality tools..."

echo "📝 Formatting code with Black..."
uv run black .

echo "✅ Code formatting completed!"
echo ""
echo "💡 To check formatting without changes, run: uv run black --check ."
echo "💡 To see what would change, run: uv run black --check --diff ."