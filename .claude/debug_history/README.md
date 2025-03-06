# Debug History Database

This directory maintains a history of debugging sessions, error-solution pairs, and implementation challenges encountered during the development of the Atlantis Go project.

## Structure

Debug entries are organized by:

1. **Component**: The system component where the issue occurred (e.g., art_system, core_user_system)
2. **Error Type**: The category of error (e.g., database, api, ui, authentication)
3. **Date**: YYYY-MM-DD format of when the issue was encountered and solved

## Entry Format

Each debug history entry includes:

- **Error Description**: What went wrong
- **Context**: Where and how the error occurred
- **Diagnosis**: The root cause analysis
- **Solution**: How the issue was fixed
- **Code Before/After**: Example of the problematic code and the fix
- **Tags**: Keywords for searchability
- **Related Issues**: Links to similar problems or dependencies

## Usage Guidelines

1. Create a new markdown file for each significant debugging session
2. Name the file using the format: `YYYY-MM-DD-component-brief-description.md`
3. Include all sections in the entry format
4. Tag the entry appropriately for future reference
5. Link related issues when patterns emerge

## Example Entry

See `2023-03-06-example-foreign-key-constraint.md` for a template example. 