#!/bin/bash

# Script to add a new Q&A entry to the Claude Optimization Layer

# Prompt for component
echo "Enter the component name (e.g., art_system, core_user_system):"
read COMPONENT

# Prompt for topic
echo "Enter the topic (e.g., model_relationship, api_design, performance):"
read TOPIC

# Create filename
FILENAME="${COMPONENT}_${TOPIC// /_}.md"
FILEPATH=".claude/qa/$FILENAME"

# Ensure the qa directory exists
mkdir -p .claude/qa

# Create the file
cat > "$FILEPATH" << EOL
# ${COMPONENT^} - ${TOPIC^} Q&A

## Question 1: [Descriptive Question Title]

**Context**: 
<!-- Describe the situation or background that led to this question -->

**Question**:
<!-- Write the specific question here -->

**Answer**:
<!-- Provide a detailed answer -->

\`\`\`python
# Example code if applicable
\`\`\`

**Benefits**:
<!-- List the benefits of this approach -->

## Question 2: [Descriptive Question Title]

**Context**: 
<!-- Describe the situation or background that led to this question -->

**Question**:
<!-- Write the specific question here -->

**Answer**:
<!-- Provide a detailed answer -->

\`\`\`python
# Example code if applicable
\`\`\`

**Benefits**:
<!-- List the benefits of this approach -->

## Question 3: [Descriptive Question Title]

**Context**: 
<!-- Describe the situation or background that led to this question -->

**Question**:
<!-- Write the specific question here -->

**Answer**:
<!-- Provide a detailed answer -->

\`\`\`python
# Example code if applicable
\`\`\`

**Benefits**:
<!-- List the benefits of this approach -->

## Related Questions

- Link to other Q&A documents with related questions
EOL

echo "Q&A template created at $FILEPATH"
echo "Please edit the file to add the specific questions and answers for the ${COMPONENT} ${TOPIC}." 