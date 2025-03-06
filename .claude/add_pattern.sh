#!/bin/bash

# Script to add a new pattern to the Claude Optimization Layer

# Prompt for pattern category
echo "Enter the pattern category (e.g., django_models, react_components, api_endpoints):"
read CATEGORY

# Prompt for pattern name
echo "Enter a pattern name (will be used in the filename):"
read NAME

# Create filename
FILENAME="${CATEGORY}_${NAME// /_}.md"
FILEPATH=".claude/patterns/$FILENAME"

# Create the file
cat > "$FILEPATH" << EOL
# ${NAME^} Patterns

## Overview

Brief description of the pattern category and its importance in the codebase.

## Common Patterns

### Pattern 1: [Name]

**Purpose**: What problem does this pattern solve?

**Implementation**:

\`\`\`python
# Example implementation
def example_code():
    pass
\`\`\`

**Key Points**:
- Important consideration 1
- Important consideration 2

**When to Use**:
- Scenario 1
- Scenario 2

**When to Avoid**:
- Anti-pattern scenario 1
- Anti-pattern scenario 2

### Pattern 2: [Name]

**Purpose**: What problem does this pattern solve?

**Implementation**:

\`\`\`python
# Example implementation
def example_code():
    pass
\`\`\`

**Key Points**:
- Important consideration 1
- Important consideration 2

**When to Use**:
- Scenario 1
- Scenario 2

**When to Avoid**:
- Anti-pattern scenario 1
- Anti-pattern scenario 2

## Uncertainty Handling

How to handle edge cases or uncertainty in these patterns.

## Error Recovery

How to recover from failures or unexpected states.

## Performance Considerations

Performance implications and optimization strategies.

## Related Patterns

- Link to related pattern documents
EOL

echo "Pattern template created at $FILEPATH"
echo "Please edit the file to add the specific details of your pattern." 