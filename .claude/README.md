# Claude Optimization Layer

This directory contains special structures and metadata to optimize the codebase for Claude AI assistance. The optimization layer enables Claude to understand, navigate, and provide assistance with the Atlantis Go codebase more efficiently.

## Purpose

The Claude Optimization Layer was created to:

1. **Enhance Understanding**: Provide Claude with structured information about the codebase architecture, relationships, and intent
2. **Improve Assistance**: Enable more accurate, context-aware recommendations and solutions
3. **Preserve Knowledge**: Document common problems, patterns, and design decisions for future reference
4. **Accelerate Development**: Make Claude more efficient at helping with implementation tasks

## Directory Structure

### Metadata (`/metadata`)

Contains normalized information about the codebase structure, organization, and classification:

- `component_dependencies.json`: Maps dependencies between major system components
- `file_classification.json`: Categorizes files by purpose (implementation, interface, test)
- `error_patterns.json`: Documents common errors and their solutions

### Code Index (`/code_index`)

Semantic indexing of code components with pre-analyzed relationships:

- `art_system.json`: Semantic relationships within the Art System component
- Additional component indices will be added as the implementation progresses

### Debug History (`/debug_history`)

Logs of debugging sessions with error-solution pairs:

- Organized by component, error type, and date
- Includes context, diagnosis, solutions, and code examples

### Patterns (`/patterns`)

Canonical implementation patterns with examples:

- `django_model_relationships.md`: Patterns for common model relationships
- Additional pattern libraries for other aspects of the codebase

### Cheatsheets (`/cheatsheets`)

Quick-reference guides for components:

- `core_user_system.md`: Common operations, gotchas, and best practices
- Additional cheatsheets for other components

### QA (`/qa`)

Database of previously solved problems and their solutions:

- Organized by component, file, and error type
- Includes context and reasoning behind solutions

### Delta (`/delta`)

Semantic change logs between versions:

- Documents API changes and their implications
- Includes reasoning behind significant changes

### Models (`/models`)

Model-friendly documentation with explicit sections:

- Purpose, schema, relationships, patterns, interfaces, invariants, and error states
- `art.md`: Documentation for the Art model

### Memory Anchors

Explicit reference points for key concepts in the codebase:

- `memory_anchors.md`: UUID-based anchors for precise referencing

## How to Use

### For Developers

1. **When adding new code**:
   - Update relevant code indices and documentation
   - Add new patterns when implementing reusable solutions
   - Document significant design decisions

2. **When fixing bugs**:
   - Add entries to the debug history
   - Update error patterns database if applicable
   - Include context and reasoning in your documentation

3. **When asking Claude for help**:
   - Reference relevant sections from this optimization layer
   - Point Claude to specific patterns or examples
   - Use memory anchors for precise referencing

### For Claude

Claude should use this optimization layer to:

1. **Improve Understanding**:
   - Reference code indices and component relationships
   - Use file classification to understand purpose
   - Leverage memory anchors for consistent referencing

2. **Provide Better Solutions**:
   - Refer to documented patterns when suggesting implementations
   - Check error patterns database when diagnosing issues
   - Use debug history to learn from previous solutions

3. **Maintain Consistency**:
   - Follow established patterns and conventions
   - Reference model documentation when discussing data structures
   - Maintain this optimization layer as the codebase evolves

## Contributing to the Optimization Layer

1. **Add New Patterns**: When you implement a reusable solution, document it in the patterns directory
2. **Document Debugging**: After solving a tricky issue, add it to the debug history
3. **Update Indices**: When adding new components, update the code index and component dependencies
4. **Add Memory Anchors**: For key concepts, add UUIDs to the memory anchors file
5. **Expand Cheatsheets**: Add common operations and gotchas to component cheatsheets

Remember, the quality of Claude's assistance depends on the quality of this optimization layer. Keep it updated and comprehensive to maximize its value. 