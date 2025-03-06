#!/bin/bash

# add_pattern_ref.sh - A script to add pattern references to files
# Usage: ./.claude/add_pattern_ref.sh <file_path> <pattern_name>
# Example: ./.claude/add_pattern_ref.sh studious_engine/core/models/user.py virtue_metrics_calculation

set -e

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <file_path> <pattern_name>"
    echo "Available patterns: matrix_flow, virtue_metrics_calculation, experience_progression, zone_geographic_patterns"
    exit 1
fi

FILE_PATH="$1"
PATTERN_NAME="$2"

# Check if the file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File $FILE_PATH does not exist."
    exit 1
fi

# Validate the pattern name
VALID_PATTERNS=("matrix_flow" "virtue_metrics_calculation" "experience_progression" "zone_geographic_patterns")
IS_VALID=0

for pattern in "${VALID_PATTERNS[@]}"; do
    if [ "$PATTERN_NAME" == "$pattern" ]; then
        IS_VALID=1
        break
    fi
done

if [ "$IS_VALID" -eq 0 ]; then
    echo "Error: Invalid pattern name. Available patterns:"
    for pattern in "${VALID_PATTERNS[@]}"; do
        echo "  - $pattern"
    done
    exit 1
fi

# Check if the pattern reference already exists
if grep -q "\[CLAUDE:CHECK_PATTERN:$PATTERN_NAME\]" "$FILE_PATH"; then
    echo "Pattern reference already exists in $FILE_PATH"
    exit 0
fi

# Find optimization layer markers or reference markers
REF_MARKER=$(grep -n "\[REF:" "$FILE_PATH" | head -1 | cut -d: -f1)
START_MARKER=$(grep -n "\[CLAUDE:OPTIMIZATION_LAYER:START\]" "$FILE_PATH" | head -1 | cut -d: -f1)

if [ -n "$REF_MARKER" ]; then
    LINE_TO_INSERT_AFTER=$REF_MARKER
elif [ -n "$START_MARKER" ]; then
    # If there's a START marker but no pattern reference, insert before END marker
    END_MARKER=$(grep -n "\[CLAUDE:OPTIMIZATION_LAYER:END\]" "$FILE_PATH" | head -1 | cut -d: -f1)
    LINE_TO_INSERT_AFTER=$(($END_MARKER - 1))
else
    # If there's no marker at all, add everything at the beginning of the file
    # First, determine if the file starts with a shebang or import
    FIRST_LINE=$(head -1 "$FILE_PATH")
    if [[ $FIRST_LINE == \#\!* || $FIRST_LINE == "from "* || $FIRST_LINE == "import "* ]]; then
        # Find the first blank line after imports
        LINE_TO_INSERT_AFTER=$(grep -n "^$" "$FILE_PATH" | head -1 | cut -d: -f1)
        if [ -z "$LINE_TO_INSERT_AFTER" ]; then
            # If no blank line, insert after the first block of imports
            LINE_TO_INSERT_AFTER=$(grep -n -v "^from\|^import\|^#" "$FILE_PATH" | head -1 | cut -d: -f1)
            LINE_TO_INSERT_AFTER=$((LINE_TO_INSERT_AFTER - 1))
        fi
    else
        LINE_TO_INSERT_AFTER=0
    fi
fi

# Determine the component from existing reference or make educated guess
if grep -q "\[REF:[^:]*:\([^]]*\)\]" "$FILE_PATH"; then
    COMPONENT=$(grep -o "\[REF:[^:]*:\([^]]*\)\]" "$FILE_PATH" | sed 's/.*:\([^]]*\)\].*/\1/g' | head -1)
else
    # Try to guess component based on file path
    if [[ "$FILE_PATH" == *"/core/"* ]]; then
        COMPONENT="CORE_USER_SYSTEM"
    elif [[ "$FILE_PATH" == *"/zones/"* ]]; then
        COMPONENT="ZONE_SYSTEM"
    elif [[ "$FILE_PATH" == *"/experiences/"* ]]; then
        COMPONENT="EXPERIENCE_SYSTEM"
    elif [[ "$FILE_PATH" == *"/market/"* || "$FILE_PATH" == *"economic"* ]]; then
        COMPONENT="ECONOMIC_SYSTEM"
    else
        COMPONENT="CORE_USER_SYSTEM"  # Default
    fi
fi

# Generate UUID anchor if none exists
if ! grep -q "\[REF:" "$FILE_PATH"; then
    case "$COMPONENT" in
        "CORE_USER_SYSTEM")
            ANCHOR_ID="00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"
            ;;
        "ZONE_SYSTEM")
            ANCHOR_ID="33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8"
            ;;
        "EXPERIENCE_SYSTEM")
            ANCHOR_ID="22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7"
            ;;
        "ECONOMIC_SYSTEM")
            ANCHOR_ID="44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9"
            ;;
        *)
            ANCHOR_ID="00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"
            ;;
    esac
    
    # If no reference exists, add it along with the pattern
    if [ "$LINE_TO_INSERT_AFTER" -eq 0 ]; then
        # Insert at beginning
        TMP_FILE=$(mktemp)
        echo "# [REF:$ANCHOR_ID:$COMPONENT]" > "$TMP_FILE"
        echo "# [CLAUDE:CHECK_PATTERN:$PATTERN_NAME]" >> "$TMP_FILE"
        echo "# [CLAUDE:OPTIMIZATION_LAYER:START]" >> "$TMP_FILE"
        echo "# This file is part of the ${COMPONENT,,} component" >> "$TMP_FILE"
        echo "# See .claude/README.md for more information" >> "$TMP_FILE"
        echo "# [CLAUDE:OPTIMIZATION_LAYER:END]" >> "$TMP_FILE"
        echo "" >> "$TMP_FILE"
        cat "$FILE_PATH" >> "$TMP_FILE"
        mv "$TMP_FILE" "$FILE_PATH"
    else
        # Insert after specified line
        sed -i "" "${LINE_TO_INSERT_AFTER}a\\
# [REF:$ANCHOR_ID:$COMPONENT]\\
# [CLAUDE:CHECK_PATTERN:$PATTERN_NAME]\\
# [CLAUDE:OPTIMIZATION_LAYER:START]\\
# This file is part of the ${COMPONENT,,} component\\
# See .claude/README.md for more information\\
# [CLAUDE:OPTIMIZATION_LAYER:END]
" "$FILE_PATH"
    fi
else
    # If reference exists but no pattern ref, add just the pattern ref
    sed -i "" "${LINE_TO_INSERT_AFTER}a\\
# [CLAUDE:CHECK_PATTERN:$PATTERN_NAME]
" "$FILE_PATH"
fi

echo "Added pattern reference for $PATTERN_NAME to $FILE_PATH"
exit 0 