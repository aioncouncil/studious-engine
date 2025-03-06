# Atlantis Go Model Mapping

This document maps the models in our refactoring plan to their implementation status in the codebase.

## Core User System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| PlayerProfile | ✅ Implemented | core/models/__init__.py | Already has economic_layer, tutorial_progress, and most required fields |
| PlayerHappiness (VirtueMetrics) | ✅ Implemented | core/models/__init__.py | Inherits from HappinessMetrics abstract class |
| UserPreferences | ✅ Implemented | core/models/__init__.py | Has interface_settings, notification_preferences, etc. |
| UserLocation | ✅ Implemented | core/models/__init__.py | Has all the required fields |

## Art System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| Art | ✅ Implemented | core/models/art/art.py | Has all the required fields |
| ArtParts | ✅ Implemented | core/models/art/art.py | Has all the required fields |
| ArtStage | ✅ Implemented | core/models/art/art.py | Has all the required fields |
| ArtTaxonomy | ✅ Implemented | core/models/art/art.py | Has all the required fields |
| TechTree | ✅ Implemented | core/models/art/tech_tree.py | Need to verify completeness |
| ArtMastery | ✅ Implemented | core/models/art/user_progress.py | Need to verify completeness |
| UserArtStageProgress | ✅ Implemented | core/models/art/user_progress.py | Need to verify completeness |
| UserTechTreeProgress | ✅ Implemented | core/models/art/user_progress.py | Need to verify completeness |

## Experience Engine

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| Experience | ✅ Implemented | experiences/models/__init__.py | Has matrix_position field with soul/body, in/out quadrants |
| ExperienceInstance | ✅ Implemented | experiences/models/__init__.py | Has matrix_flow_data, current_matrix_phase fields |
| ExperienceParticipation | ✅ Implemented | experiences/models/__init__.py | Tracks individual participation in experiences |
| PlayerExperience | ✅ Implemented | experiences/models/__init__.py | Tracks player's individual experience journey |
| Power | ✅ Implemented | experiences/models/__init__.py | Skills/ideas players can master (like Pokemon) |
| PlayerPower | ✅ Implemented | experiences/models/__init__.py | Player's acquired powers and mastery levels |
| Artifact | ✅ Implemented | core/models/__init__.py | Has all the required fields |
| MediaAsset | ✅ Implemented | core/models/__init__.py | Has all the required fields |

## Zone System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| Zone | ✅ Implemented | zones/models/__init__.py | Has basic fields but needs economy enhancements |
| Sector | ✅ Implemented | zones/models/__init__.py | Has the 12 sectors of the city |
| ZoneHappiness | ✅ Implemented | zones/models/__init__.py | Extends HappinessMetrics for zones |
| PlayerZoneContribution | ✅ Implemented | zones/models/__init__.py | Tracks player contributions to zones |
| ZoneHierarchy | ✅ Implemented | zones/models/__init__.py | Defines hierarchical relationships between zones |
| ZoneMembership | ✅ Implemented | zones/models/__init__.py | Tracks player membership in zones with roles and permissions |
| ZoneResources | ✅ Implemented | zones/models/__init__.py | Tracks resources available in a zone |
| ResourceFlow | ✅ Implemented | zones/models/__init__.py | Manages resource movement between zones |
| ZoneActivity | ✅ Implemented | zones/models/__init__.py | Records events, projects, and initiatives in zones |
| ZoneRaid | ✅ Implemented | zones/models/__init__.py | Models raids between zones for resources or territory |
| ZoneDeficiency | ✅ Implemented | zones/models/__init__.py | Tracks resource or capability shortages in zones |

## Economic System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| Resource | ✅ Implemented | economic/models/__init__.py | Complete resource model with economic properties |
| ResourceInventory | ✅ Implemented | economic/models/__init__.py | Tracks resource ownership with generic relations |
| MarketListing | ✅ Implemented | core/models/__init__.py | Called MarketItem, has all the required fields |
| Wishlist | ✅ Implemented | core/models/__init__.py | For market items |
| EconomicTransaction | ✅ Implemented | economic/models/__init__.py | Tracks all economic transactions with context |
| WealthClass | ✅ Implemented | economic/models/__init__.py | Defines economic stratification with benefits |
| CommonResource | ✅ Implemented | economic/models/__init__.py | Manages collective resources with sustainability metrics |
| Project | ✅ Implemented | economic/models/__init__.py | Enables collective endeavors with resource management |
| ProjectParticipation | ✅ Implemented | economic/models/__init__.py | Tracks contributions and rewards for projects |

## Innovation System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| InnovationProcess | ✅ Implemented | innovations/models/__init__.py | Follows Vitruvian Innovation Loop |
| Innovation | ✅ Implemented | innovations/models/__init__.py | Similar to InnovationProcess |
| InnovationContribution | ✅ Implemented | innovations/models/__init__.py | Tracks contributions to Innovation |

## Physics System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| PhysicsSimulation | ✅ Implemented | physics/models.py | Has all the required fields |
| PhysicsInteraction | ✅ Implemented | physics/models.py | Tracks user progress through simulations |

## AI Guide System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| UserGoal | ❌ Missing | - | Needs to be implemented |
| AiInteraction | ❌ Missing | - | Needs to be implemented |
| HappinessRecommendation | ❌ Missing | - | Needs to be implemented |
| ArtProposal | ❌ Missing | - | Needs to be implemented |

## Meta-Governance System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| MetaRole | ❌ Missing | - | Needs to be implemented |
| MetaRoleAssignment | ❌ Missing | - | Needs to be implemented |
| GovernanceAction | ❌ Missing | - | Needs to be implemented |
| Decision | ❌ Missing | - | Needs to be implemented |
| Election | ❌ Missing | - | Needs to be implemented |
| Candidacy | ❌ Missing | - | Needs to be implemented |

## Game Mechanics System

| Model | Status | Location | Notes |
|-------|--------|----------|-------|
| Achievement | ❌ Missing | - | Needs to be implemented |
| UserAchievement | ❌ Missing | - | Needs to be implemented |
| Event | ❌ Missing | - | Needs to be implemented |
| UserActivity | ❌ Missing | - | Needs to be implemented |

## Implementation Priorities

Based on the above mapping, the following models should be implemented in order:

1. ✅ **Zone System Enhancements** - COMPLETED
   - ZoneHierarchy, ZoneMembership, ZoneResources, ResourceFlow, ZoneActivity, ZoneRaid, ZoneDeficiency

2. ✅ **Economic System** - COMPLETED
   - Resource, ResourceInventory, EconomicTransaction, WealthClass, CommonResource, Project, ProjectParticipation

3. **AI Guide System** - NEXT PRIORITY
   - UserGoal, AiInteraction, HappinessRecommendation, ArtProposal

4. **Meta-Governance System**
   - MetaRole, MetaRoleAssignment, GovernanceAction, Decision, Election, Candidacy

5. **Game Mechanics System**
   - Achievement, UserAchievement, Event, UserActivity

This prioritization aligns with the phases in our refactoring plan, starting with enhancing the Zone System (Phase 4), then implementing the Economic System (Phase 5), and so on. 