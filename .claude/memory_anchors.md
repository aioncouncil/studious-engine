# Memory Anchors for Atlantis Go Codebase

This file contains explicit memory anchors that Claude can reference when working with the Atlantis Go codebase. Each anchor has a unique UUID and semantic structure to facilitate precise recall.

## Project Structure Anchors

### Core Components

- **[ANCHOR:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]**
  The Core User System is the foundation of Atlantis Go, handling user profiles, virtue metrics, preferences, and location tracking. This system is implemented in Phase 1.

- **[ANCHOR:11b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6:ART_SYSTEM]**
  The Art System is the "Pokédex" of Atlantis Go, allowing users to collect, categorize, practice, and master different types of human creative endeavors. This system is implemented in Phase 2.

- **[ANCHOR:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]**
  The Experience System is the engine for creating, discovering, and participating in experiences. This system is implemented in Phase 3.

- **[ANCHOR:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]**
  The Zone System manages geographic and functional areas for activities and governance. This system is implemented in Phase 4.

- **[ANCHOR:44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9:ECONOMIC_SYSTEM]**
  The Economic System handles resources, marketplace, and economic layers (Port, Laws, Republic). This system is implemented in Phase 5.

### Key Concepts

- **[ANCHOR:55f6a7b8-c9d0-e1f2-a3b4-c5d6e7f8a9b0:MATRIX_FLOW]**
  The Matrix Flow is the fundamental process model in Atlantis Go, following the sequence: Soul Out → Body Out → Soul In → Body In. This concept appears across multiple systems.

- **[ANCHOR:66a7b8c9-d0e1-f2a3-b4c5-d6e7f8a9b0c1:VIRTUE_METRICS]**
  Virtue Metrics are the core measurements of user progress in Atlantis Go, including wisdom, courage, temperance, justice, strength, health, beauty, and endurance.

- **[ANCHOR:77b8c9d0-e1f2-a3b4-c5d6-e7f8a9b0c1d2:TECH_TREE]**
  The Tech Tree is the progression system linking arts, experiences, and unlockables in a hierarchical relationship structure.

- **[ANCHOR:88c9d0e1-f2a3-b4c5-d6e7-f8a9b0c1d2e3:FIVE_PART_STRUCTURE]**
  The Five-Part Structure (Definition, End, Parts, Matter, Instrument) is the foundational learning framework for arts in Atlantis Go, based on Aristotle's five causes.

## Model Relationship Anchors

- **[ANCHOR:99d0e1f2-a3b4-c5d6-e7f8-a9b0c1d2e3f4:USER_PROFILE_RELATIONSHIPS]**
  User → PlayerProfile (1:1)
  PlayerProfile → PlayerHappiness (1:1)
  PlayerProfile → UserPreferences (1:1)
  PlayerProfile → UserLocation (1:1)

- **[ANCHOR:aae1f2a3-b4c5-d6e7-f8a9-b0c1d2e3f4a5:ART_SYSTEM_RELATIONSHIPS]**
  Art → ArtParts (1:many)
  Art → ArtStage (1:many)
  Art ↔ Art (many:many) via parent_arts
  Art → ArtTaxonomy (many:one)
  Art ↔ TechTree (many:many) via required_arts and unlocks_arts
  User → ArtMastery → Art (many:many)

- **[ANCHOR:bbf2a3b4-c5d6-e7f8-a9b0-c1d2e3f4a5b6:ZONE_SYSTEM_RELATIONSHIPS]**
  Zone → Sector (1:many)
  Zone → ZoneHierarchy (1:many)
  User ↔ Zone (many:many) via ZoneMembership
  Zone → ZoneResources (1:many)
  Zone → ZoneActivity (1:many)

## Implementation Phase Anchors

- **[ANCHOR:cca3b4c5-d6e7-f8a9-b0c1-d2e3f4a5b6c7:PHASE1_CORE_USER_SYSTEM]**
  Phase 1 implements the Core User System, including User profiles, happiness metrics, preferences, and location tracking.

- **[ANCHOR:ddb4c5d6-e7f8-a9b0-c1d2-e3f4a5b6c7d8:PHASE2_ART_SYSTEM]**
  Phase 2 implements the Art System, the "Pokédex" that allows users to collect and master creative practices.

- **[ANCHOR:eec5d6e7-f8a9-b0c1-d2e3-f4a5b6c7d8e9:PHASE3_EXPERIENCE_ENGINE]**
  Phase 3 implements the Experience Engine, handling the creation and participation in experiences.

- **[ANCHOR:ffd6e7f8-a9b0-c1d2-e3f4-a5b6c7d8e9f0:PHASE4_ZONE_SYSTEM]**
  Phase 4 implements the Zone System, managing geographic and functional areas.

- **[ANCHOR:00e7f8a9-b0c1-d2e3-f4a5-b6c7d8e9f0a1:PHASE5_ECONOMIC_SYSTEM]**
  Phase 5 implements the Economic System, handling resources and marketplace functions.

## UI Component Anchors

- **[ANCHOR:11f8a9b0-c1d2-e3f4-a5b6-c7d8e9f0a1b2:MAIN_MAP_SCREEN]**
  The Main Map Screen is the home screen, equivalent to the Pokémon Go main map, showing nearby arts, zones, and experiences.

- **[ANCHOR:22a9b0c1-d2e3-f4a5-b6c7-d8e9f0a1b2c3:ART_COLLECTION_SCREEN]**
  The Art Collection Screen is equivalent to the Pokédex, showing all discovered and undiscovered arts.

- **[ANCHOR:33b0c1d2-e3f4-a5b6-c7d8-e9f0a1b2c3d4:ART_CAPTURE_SCREEN]**
  The Art Capture Screen is equivalent to the Pokémon catch screen, showing the AR view for discovering arts.

- **[ANCHOR:44c1d2e3-f4a5-b6c7-d8e9-f0a1b2c3d4e5:ZONE_VIEW_SCREEN]**
  The Zone View Screen is equivalent to the Gym/PokéStop interaction, showing zone information and activities.

- **[ANCHOR:55d2e3f4-a5b6-c7d8-e9f0-a1b2c3d4e5f6:PROFILE_SCREEN]**
  The Profile Screen is equivalent to the Trainer profile, showing user information, virtue metrics, and achievements.

## API Endpoint Anchors

- **[ANCHOR:66e3f4a5-b6c7-d8e9-f0a1-b2c3d4e5f6a7:USER_API_ENDPOINTS]**
  User-related API endpoints for authentication, profile management, and preference settings.

- **[ANCHOR:77f4a5b6-c7d8-e9f0-a1b2-c3d4e5f6a7b8:ART_API_ENDPOINTS]**
  Art-related API endpoints for discovering, viewing, and practicing arts.

- **[ANCHOR:88a5b6c7-d8e9-f0a1-b2c3-d4e5f6a7b8c9:EXPERIENCE_API_ENDPOINTS]**
  Experience-related API endpoints for creating, joining, and completing experiences.

- **[ANCHOR:99b6c7d8-e9f0-a1b2-c3d4-e5f6a7b8c9d0:ZONE_API_ENDPOINTS]**
  Zone-related API endpoints for joining zones, participating in activities, and zone management.

- **[ANCHOR:aac7d8e9-f0a1-b2c3-d4e5-f6a7b8c9d0e1:ECONOMIC_API_ENDPOINTS]**
  Economic API endpoints for resource management, marketplace interactions, and economic governance.

## File Structure Anchors

- **[ANCHOR:bbd8e9f0-a1b2-c3d4-e5f6-a7b8c9d0e1f2:DOCUMENTATION_LOCATION]**
  Documentation files are primarily located in the `/docs` directory, with transformation plans in `/docs/transformation/`.

- **[ANCHOR:cce9f0a1-b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4:CLAUDE_OPTIMIZATION_STRUCTURE]**
  Claude optimization files are located in the `/.claude` directory, organized into metadata, code_index, debug_history, patterns, cheatsheets, qa, and delta.

- **[ANCHOR:ddf0a1b2-c3d4-e5f6-a7b8-c9d0e1f2a3b4:CORE_CODE_LOCATION]**
  Core implementation code is located in the `/studious_engine` directory, which will be transformed into the Atlantis Go implementation.

## Database Structure Anchors

- **[ANCHOR:eea1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:DATABASE_SCHEMA_OVERVIEW]**
  The database schema follows Django's model system, with tables corresponding to each model and relationship tables for many-to-many relationships.

- **[ANCHOR:ffb2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6:JSON_FIELD_USAGE]**
  JSON fields are used throughout the application for flexible storage of structured data, particularly for progress tracking, configuration settings, and virtue history.

## Error Handling Anchors

- **[ANCHOR:00c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:COMMON_ERROR_PATTERNS]**
  Common error patterns and their solutions are documented in `.claude/metadata/error_patterns.json`.

- **[ANCHOR:11d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:DEBUG_HISTORY_STRUCTURE]**
  Debugging history and solutions are documented in the `.claude/debug_history/` directory, organized by component and error type. 