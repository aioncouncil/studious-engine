# Art System Implementation Delta Summary

## Overview

This document outlines the major changes and additions required to implement the Art System (Phase 2) in the Atlantis Go project. The Art System serves as the "Pokédex" of Atlantis Go, allowing users to collect, categorize, practice, and master different types of human creative endeavors.

## Current State → Target State

The Art System is **completely missing** from the current EudaimoniaGo implementation and needs to be created from scratch. This represents a significant addition of new models, relationships, business logic, and UI components.

## Model Changes

### New Models Added

1. **Art**
   - Base model representing a creative practice
   - Major fields: name, description, taxonomy, difficulty, requirements
   - Key relationships: parent_arts (M2M), taxonomy (FK)

2. **ArtPart**
   - Components or aspects of an art that must be practiced
   - Major fields: name, order_index, practice_method, validation_method
   - Key relationships: art (FK)

3. **ArtMastery**
   - Tracks a user's mastery of a specific art
   - Major fields: mastery_level, practice_streak, completed_parts (JSON)
   - Key relationships: user (FK), art (FK), current_part (FK)

4. **ArtStage**
   - Represents different learning stages for an art
   - Major fields: name, order_index, mastery_threshold, virtue_bonuses
   - Key relationships: art (FK)

5. **UserArtStageProgress**
   - Tracks a user's progress through art stages
   - Major fields: reached_date, is_current, completion_percentage
   - Key relationships: user (FK), art_stage (FK)

6. **ArtTaxonomy**
   - Categorization system for arts
   - Major fields: name, level, path, parent (self-reference)
   - Key relationships: parent (FK to self)

7. **TechTree**
   - Technology tree linking arts progression
   - Major fields: name, level, required_resources, zone requirements
   - Key relationships: required_arts (M2M), unlocks_arts (M2M)

8. **UserTechTreeProgress**
   - Tracks a user's progress through the tech tree
   - Major fields: unlocked_date, progress_percentage, missing_requirements
   - Key relationships: user (FK), tech_tree (FK)

### API Changes

Added new REST endpoints for:

1. Art collection and discovery
2. Art part progression
3. Mastery tracking
4. Tech tree visualization
5. Taxonomy browsing

### Schema Migrations

1. Create tables for all 8 new models
2. Create appropriate indexes for common query patterns
3. Set up foreign key relationships and constraints
4. Add initial seed data for arts and taxonomy

## Behavioral Changes

### New Features

1. **Art Discovery**
   - Users can discover new arts based on:
     - Geographic location
     - Completed prerequisites
     - Tech tree unlocks

2. **Art Practice**
   - Users can practice arts through their component parts
   - Progress is tracked and validated according to part requirements
   - Practice increases mastery level and contributes to virtue scores

3. **Art Mastery**
   - Users progress through stages of mastery
   - Completed arts provide ongoing virtue bonuses
   - Mastery unlocks new arts in the tech tree

4. **Tech Tree Progression**
   - Visual representation of art relationships
   - Unlock paths for discovering new arts
   - Prerequisites display with progress indicators

### Changed Behaviors

1. **User Profile**
   - Now includes art collection statistics
   - Shows featured/mastered arts
   - Virtue metrics affected by art practice

2. **Experience System Integration**
   - Experiences can now require specific arts
   - Experiences can contribute to art mastery
   - Art practice can generate artifacts

## UI Changes

1. **New Screens**
   - Art Collection (Pokédex)
   - Art Detail with five-part structure
   - Art Capture interface
   - Art Practice workflow
   - Tech Tree visualization

2. **Modified Screens**
   - User Profile
   - Main Map (showing art discovery opportunities)
   - Experience creation (art requirements)

## Performance Considerations

1. **Query Optimizations**
   - Added indexes on user_id + art_id combinations
   - Preloading of art relationships for common views
   - Denormalized some data for faster retrieval

2. **Caching Strategy**
   - Art taxonomies and tech tree cached heavily (rarely change)
   - User mastery summaries cached with timeout
   - Unlocked status computed and cached

## Security Impact

1. **New Permissions**
   - Art visibility based on user rank and economic layer
   - Practice validation authorization
   - Mastery validation controls

2. **Data Validation**
   - Enforced mastery progression rules
   - Tech tree unlocking requirements validated server-side
   - Practice session validation with anti-cheat measures

## Migration Strategy

1. **Development Approach**
   - Create models and base functionality first
   - Implement API endpoints with tests
   - Develop UI components
   - Add tech tree visualization last

2. **Testing Strategy**
   - Unit tests for model logic
   - API tests for endpoint functionality
   - Integration tests for user workflows
   - Performance tests for collection views

3. **Deployment Strategy**
   - Feature flag all Art System components
   - Deploy database migrations first
   - Gradual rollout of UI components
   - Monitor performance metrics

## Reasoning

The Art System implementation follows the "Pokédex" design pattern to create a compelling collection and mastery mechanic that drives user engagement. Key design decisions:

1. **Five-part Learning Structure**
   - Based on Aristotle's five causes
   - Creates a consistent learning framework
   - Facilitates partial progress and clear goals

2. **Tech Tree Approach**
   - Provides clear progression paths
   - Creates dependencies that guide learning
   - Rewards mastery with new discoveries

3. **JSON Fields for Flexibility**
   - Used for tracking progress and requirements
   - Allows for custom attributes per art
   - Simplifies schema for evolving requirements

4. **Self-referential Taxonomy**
   - Enables unlimited categorization depth
   - Allows arts to appear in multiple contexts
   - Maintains hierarchy for browsing

## API Example

New endpoint for discovering an art:

```
POST /api/arts/{art_id}/discover/
```

Response:
```json
{
  "success": true,
  "mastery": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "art": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Poetry",
      "description": "The art of rhythmical composition...",
      "icon": "/media/icons/poetry.png"
    },
    "discovery_date": "2023-03-06T12:34:56Z",
    "mastery_level": 0,
    "current_part": {
      "id": "7a1b9cde-f234-56e7-89ab-cdef01234567",
      "name": "Definition",
      "order_index": 1
    },
    "progress_percentage": 0
  },
  "virtue_updates": {
    "wisdom": 1,
    "beauty": 1
  }
}
``` 