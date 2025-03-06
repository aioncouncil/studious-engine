# Claude Optimization Layer Helper Scripts

This directory contains several helper scripts to make it easier to maintain the Claude Optimization Layer. These scripts automate the creation of properly formatted entries in the various directories of the optimization layer.

## Available Scripts

### `add_debug_entry.sh`

**Purpose**: Creates a new debug history entry with proper formatting.

**Usage**:
```bash
./.claude/add_debug_entry.sh
```

**Interactive Prompts**:
1. Component name (e.g., art_system, core_user_system)
2. Error type (e.g., database, api, ui)
3. Brief description (used in filename)

The script creates a properly formatted Markdown file in the `.claude/debug_history/` directory with the correct date, headers, and sections.

### `add_pattern.sh`

**Purpose**: Creates a new pattern documentation file with proper formatting.

**Usage**:
```bash
./.claude/add_pattern.sh
```

**Interactive Prompts**:
1. Pattern category (e.g., django_models, react_components)
2. Pattern name (used in filename)

The script creates a properly formatted Markdown file in the `.claude/patterns/` directory with all the required sections for documenting a pattern.

### `add_model_doc.sh`

**Purpose**: Creates a new model-friendly documentation file with proper formatting.

**Usage**:
```bash
./.claude/add_model_doc.sh
```

**Interactive Prompts**:
1. Model name (e.g., User, Art, PlayerProfile)

The script creates a properly formatted Markdown file in the `.claude/models/` directory with all the required sections for model documentation.

## How to Use These Scripts

1. First, make sure the scripts are executable:
   ```bash
   chmod +x .claude/*.sh
   ```

2. Run the desired script from the project root:
   ```bash
   ./.claude/add_debug_entry.sh
   ```

3. Follow the interactive prompts to provide the required information.

4. The script will create a new file with the appropriate template.

5. Edit the generated file to add your specific content.

## Extending These Scripts

If you need to add more scripts to the Claude Optimization Layer, please follow these guidelines:

1. Name the script descriptively with the pattern `add_[type].sh`
2. Make the script executable with `chmod +x`
3. Use interactive prompts to gather necessary information
4. Generate properly formatted files with all required sections
5. Add the script to this documentation file

Remember that consistent documentation and organization are key to maintaining an effective Claude Optimization Layer. 