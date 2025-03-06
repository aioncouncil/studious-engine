#!/bin/bash

# Script to add new model-friendly documentation to the Claude Optimization Layer

# Prompt for model name
echo "Enter the model name (e.g., User, Art, PlayerProfile):"
read MODEL_NAME

# Create filename
FILENAME="${MODEL_NAME,,}.md"
FILEPATH=".claude/models/$FILENAME"

# Ensure the models directory exists
mkdir -p .claude/models

# Create the file
cat > "$FILEPATH" << EOL
# ${MODEL_NAME} Model

## Purpose

<!-- Describe what this model represents and why it exists -->

The ${MODEL_NAME} model is responsible for...

## Schema

### Fields

| Field Name | Type | Description | Constraints |
|------------|------|-------------|------------|
| id | AutoField | Primary key | Auto-incrementing |
| field1 | Type | Description | Constraints |
| field2 | Type | Description | Constraints |
| field3 | Type | Description | Constraints |

### Relationships

| Relationship | Related Model | Type | Description |
|--------------|---------------|------|-------------|
| relationship1 | Model | OneToMany | Description |
| relationship2 | Model | ManyToMany | Description |

## Patterns

### Creation

\`\`\`python
# How to create a new instance
def create_${MODEL_NAME,,}():
    # Example code
    pass
\`\`\`

### Queries

\`\`\`python
# Common query patterns
def query_${MODEL_NAME,,}():
    # Example code
    pass
\`\`\`

### Updates

\`\`\`python
# How to update an instance
def update_${MODEL_NAME,,}():
    # Example code
    pass
\`\`\`

### Deletion

\`\`\`python
# How to safely delete an instance
def delete_${MODEL_NAME,,}():
    # Example code
    pass
\`\`\`

## Interfaces

### Main Properties

- \`property1\`: Description
- \`property2\`: Description

### Public Methods

- \`method1\`: Description
- \`method2\`: Description

## Invariants

The following invariants must be maintained:

1. Invariant 1
2. Invariant 2
3. Invariant 3

## Error States

### Error Type 1

- **Cause**: What causes this error
- **Detection**: How to detect it
- **Resolution**: How to resolve it

### Error Type 2

- **Cause**: What causes this error
- **Detection**: How to detect it
- **Resolution**: How to resolve it
EOL

echo "Model documentation template created at $FILEPATH"
echo "Please edit the file to add the specific details of the ${MODEL_NAME} model." 