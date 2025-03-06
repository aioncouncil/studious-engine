#!/bin/bash

# Script to check the health of the Claude Optimization Layer
# This validates references and ensures all components are properly linked

echo "Checking Claude Optimization Layer health..."

# Check for missing references
PYTHON_FILES=$(find studious_engine -type f -name "*.py" | wc -l)
REFERENCED_FILES=$(grep -r "\[REF:" --include="*.py" studious_engine | wc -l)

echo "Python files: $PYTHON_FILES"
echo "Referenced files: $REFERENCED_FILES"
echo "Coverage: $(($REFERENCED_FILES * 100 / $PYTHON_FILES))%"

# Check for missing patterns
echo -e "\nChecking pattern references:"
grep -r "\[CLAUDE:CHECK_PATTERN:" --include="*.py" studious_engine | sed 's/.*\[CLAUDE:CHECK_PATTERN:\([^]]*\)\].*/\1/g' | sort | uniq -c

# Check component coverage
echo -e "\nChecking component coverage:"
grep -r "\[REF:" --include="*.py" studious_engine | sed 's/.*\[REF:[^:]*:\([^]]*\)\].*/\1/g' | sort | uniq -c

echo -e "\nHealth check complete!"
