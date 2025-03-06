#!/bin/bash

# Script to manually add an optimization reference to a file

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <file_path> <component>"
  echo "Components: core_user_system, art_system, experience_system, zone_system, economic_system"
  exit 1
fi

FILE=$1
COMPONENT=$2

# Validate component
case $COMPONENT in
  core_user_system)
    ANCHOR_ID="00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"
    ;;
  art_system)
    ANCHOR_ID="11b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
    ;;
  experience_system)
    ANCHOR_ID="22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7"
    ;;
  zone_system)
    ANCHOR_ID="33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8"
    ;;
  economic_system)
    ANCHOR_ID="44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9"
    ;;
  *)
    echo "Invalid component: $COMPONENT"
    echo "Valid components: core_user_system, art_system, experience_system, zone_system, economic_system"
    exit 1
    ;;
esac

# Check if file exists
if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

# Create reference
COMPONENT_UPPER=$(echo "$COMPONENT" | tr '[:lower:]' '[:upper:]')
REF="# [REF:$ANCHOR_ID:$COMPONENT_UPPER]"
REF="$REF\n# [CLAUDE:OPTIMIZATION_LAYER:START]\n# This file is part of the $COMPONENT component\n# See .claude/README.md for more information\n# [CLAUDE:OPTIMIZATION_LAYER:END]"

# Add reference to file
TMP_FILE="${FILE}.tmp"
echo -e "$REF\n\n$(cat "$FILE")" > "$TMP_FILE"
mv "$TMP_FILE" "$FILE"

echo "Added reference to $FILE for component $COMPONENT"
