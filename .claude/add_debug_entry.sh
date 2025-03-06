#!/bin/bash

# Script to add a new debug history entry to the Claude Optimization Layer

# Get current date
DATE=$(date +"%Y-%m-%d")

# Prompt for component
echo "Enter the component name (e.g., art_system, core_user_system):"
read COMPONENT

# Prompt for error type
echo "Enter the error type (e.g., database, api, ui):"
read ERROR_TYPE

# Prompt for brief description
echo "Enter a brief description (will be used in the filename):"
read DESCRIPTION

# Create filename
FILENAME="${DATE}-${COMPONENT}-${DESCRIPTION// /-}.md"
FILEPATH=".claude/debug_history/$FILENAME"

# Create the file
cat > "$FILEPATH" << EOL
# ${DESCRIPTION^}

**Date**: ${DATE}  
**Component**: ${COMPONENT}  
**Error Type**: ${ERROR_TYPE}  

## Error Description

\`\`\`
Paste the error message here
\`\`\`

## Context

Describe where and how the error occurred.

## Diagnosis

Explain the root cause analysis.

## Solution

Describe how the issue was fixed.

## Code Before/After

\`\`\`python
# Before
# Paste problematic code here
\`\`\`

\`\`\`python
# After
# Paste fixed code here
\`\`\`

## Tags

\`tag1\`, \`tag2\`, \`tag3\`

## Related Issues

- Link to similar problems or dependencies
EOL

echo "Debug history entry created at $FILEPATH"
echo "Please edit the file to add the specific details of your debug session." 