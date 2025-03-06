#!/bin/bash

# Script to implement Claude Optimization Layer references across the codebase
# This script adds special comments and references to the Claude memory anchors
# throughout the codebase to create a self-improving optimization loop

echo "Starting Claude Optimization Layer implementation..."

# Ensure the script is run from the project root
if [ ! -d ".claude" ]; then
  echo "Error: Please run this script from the project root (where the .claude directory exists)"
  exit 1
fi

# Create a log file
LOG_FILE=".claude/optimization_implementation.log"
echo "Implementation started at $(date)" > $LOG_FILE

# Function to convert string to uppercase
to_uppercase() {
  echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Function to add optimization references to Python files
add_references_to_python_file() {
  local file=$1
  local basename=$(basename "$file")
  local component=""
  
  # Determine component based on path
  if [[ $file == *"core"* ]]; then
    component="core_user_system"
  elif [[ $file == *"art_system"* ]]; then
    component="art_system"
  elif [[ $file == *"experiences"* ]]; then
    component="experience_system"
  elif [[ $file == *"zones"* ]]; then
    component="zone_system"
  elif [[ $file == *"market"* || $file == *"economy"* ]]; then
    component="economic_system"
  fi
  
  # Skip if component not determined
  if [ -z "$component" ]; then
    return
  fi
  
  # Get file type
  local file_type=""
  if [[ $basename == "models.py" || $basename == *"model"* ]]; then
    file_type="model"
  elif [[ $basename == "views.py" || $basename == *"view"* ]]; then
    file_type="interface"
  elif [[ $basename == "services.py" || $basename == *"service"* ]]; then
    file_type="service"
  elif [[ $basename == *"test"* ]]; then
    file_type="test"
  else
    file_type="implementation"
  fi
  
  # Add memory anchor reference based on component and file type
  local anchor_id=""
  case $component in
    core_user_system)
      anchor_id="00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5"
      ;;
    art_system)
      anchor_id="11b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
      ;;
    experience_system)
      anchor_id="22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7"
      ;;
    zone_system)
      anchor_id="33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8"
      ;;
    economic_system)
      anchor_id="44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9"
      ;;
  esac
  
  # Add pattern reference based on file content
  local pattern_refs=""
  if grep -q "matrix" "$file"; then
    pattern_refs="$pattern_refs\n# [CLAUDE:CHECK_PATTERN:matrix_flow]"
  fi
  if grep -q "virtue" "$file"; then
    pattern_refs="$pattern_refs\n# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]"
  fi
  if grep -q "experience" "$file"; then
    pattern_refs="$pattern_refs\n# [CLAUDE:CHECK_PATTERN:experience_progression]"
  fi
  if grep -q "zone" "$file" && grep -q "geo\|location\|area" "$file"; then
    pattern_refs="$pattern_refs\n# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]"
  fi
  
  # Create the reference to add
  local component_upper=$(to_uppercase "$component")
  local ref="# [REF:$anchor_id:$component_upper]"
  if [ ! -z "$pattern_refs" ]; then
    ref="$ref$pattern_refs"
  fi
  ref="$ref\n# [CLAUDE:OPTIMIZATION_LAYER:START]\n# This file is part of the $component component\n# See .claude/README.md for more information\n# [CLAUDE:OPTIMIZATION_LAYER:END]"
  
  # Check if file already has references
  if grep -q "\[REF:" "$file"; then
    echo "Skipping $file - already has references" >> $LOG_FILE
    return
  fi
  
  # Add the reference to the top of the file after any existing imports
  # This is tricky to do with sed, so we'll create a temporary file
  local tmp_file="${file}.tmp"
  local imports_end_line=$(grep -n "^import\|^from" "$file" | tail -1 | cut -d: -f1)
  
  if [ -z "$imports_end_line" ]; then
    # No imports found, add after any shebang or encoding lines
    imports_end_line=$(grep -n "^#!.*\|^# -\*-" "$file" | tail -1 | cut -d: -f1)
    
    if [ -z "$imports_end_line" ]; then
      # No shebang or encoding lines, add to the top
      echo -e "$ref\n\n$(cat "$file")" > "$tmp_file"
    else
      # Add after shebang or encoding line
      head -n "$imports_end_line" "$file" > "$tmp_file"
      echo -e "\n$ref" >> "$tmp_file"
      tail -n +$((imports_end_line + 1)) "$file" >> "$tmp_file"
    fi
  else
    # Add after imports
    head -n "$imports_end_line" "$file" > "$tmp_file"
    echo -e "\n$ref" >> "$tmp_file"
    tail -n +$((imports_end_line + 1)) "$file" >> "$tmp_file"
  fi
  
  # Replace original file with temporary file
  mv "$tmp_file" "$file"
  echo "Added references to $file" >> $LOG_FILE
}

# Function to add optimization references to HTML templates
add_references_to_template() {
  local file=$1
  
  # Skip if already has references
  if grep -q "CLAUDE:OPTIMIZATION_LAYER" "$file"; then
    echo "Skipping $file - already has references" >> $LOG_FILE
    return
  fi
  
  # Determine component based on path
  local component=""
  if [[ $file == *"core"* ]]; then
    component="core_user_system"
  elif [[ $file == *"art_system"* ]]; then
    component="art_system"
  elif [[ $file == *"experiences"* ]]; then
    component="experience_system"
  elif [[ $file == *"zones"* ]]; then
    component="zone_system"
  elif [[ $file == *"market"* || $file == *"economy"* ]]; then
    component="economic_system"
  fi
  
  # Skip if component not determined
  if [ -z "$component" ]; then
    return
  fi
  
  # Create the reference to add
  local ref="{% comment %}\n[CLAUDE:OPTIMIZATION_LAYER:START]\nThis template is part of the $component component\nSee .claude/README.md for more information\n[CLAUDE:OPTIMIZATION_LAYER:END]\n{% endcomment %}"
  
  # Add the reference to the top of the file
  echo -e "$ref\n\n$(cat "$file")" > "${file}.tmp"
  mv "${file}.tmp" "$file"
  echo "Added references to $file" >> $LOG_FILE
}

# Find and process Python files
echo "Adding references to Python files..."
find studious_engine -type f -name "*.py" | while read -r file; do
  add_references_to_python_file "$file"
done

# Find and process HTML template files
echo "Adding references to HTML templates..."
find studious_engine -type f -name "*.html" | while read -r file; do
  add_references_to_template "$file"
done

# Create a helper script to check optimization layer health
cat > .claude/check_optimization_health.sh << 'EOL'
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
EOL

chmod +x .claude/check_optimization_health.sh

# Create a helper script to add a new reference manually
cat > .claude/add_optimization_ref.sh << 'EOL'
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
EOL

chmod +x .claude/add_optimization_ref.sh

echo "Implementation complete!"
echo "Run './.claude/check_optimization_health.sh' to check the health of the optimization layer"
echo "Use './.claude/add_optimization_ref.sh <file_path> <component>' to manually add references to specific files" 