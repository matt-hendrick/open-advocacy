# Open Advocacy Implementation Plan - FastAPI + React TypeScript Approach

## 1. Project Overview

Open Advocacy is an open-source platform connecting citizens with representatives and tracking advocacy projects. This plan outlines our FastAPI backend with a flexible database layer and React+TypeScript+Vite frontend.

## 2. Current Implementation Status

- ✅ **Backend**: FastAPI application with Pydantic models and in-memory storage
- ✅ **Frontend**: React+TypeScript+Vite application with UI components
- ✅ **Core Components**: Project listing and representative lookup functionality
- ✅ **Data Flow**: Initial implementation of frontend-backend connection
- ✅ **Database**: Setup flexible database provider system that supports Sqlite or postgres
- ⏳ **Representative Lookup Feature**: Functionality pending
- ⏳ **Auth and Admin User Features**: Functionality pending
- ⏳ **Deployment Process Setup**: Pending

## 3. Core Concepts & Data Model

### Projects
- **Core Properties**: title, description, status, link field
- **Relationships**: Associated with one or many jurisdictions
- **Status Preferences**: Each project has a preferred status goal for entities
- **Template Responses**: Can include template advocacy language (future feature)
- **Vote Aggregation**: Display color-coded distribution of entity positions

### Entity Status Types
- **Five Default Status Types**:
  - Solid Approval
  - Leaning Approval
  - Neutral
  - Leaning Disapproval
  - Solid Disapproval
- **Visual Representation**: Color-coded for quick visual assessment
- **Aggregate Display**: Projects show distribution of entity positions

### Roles & Permissions
- **Admin**: Can create/edit projects, update entity statuses, manage system
- **Anonymous Users**: Can view projects, lookup representatives, see status distributions
- **Future**: Entity-specific notes and more granular permission system

## 4. Initial Development Phases

### Phase 1: Core Functionality Prototypes (COMPLETED)
- ✅ FastAPI backend structure with routes and models
- ✅ React frontend with TypeScript and Vite
- ✅ Basic UI components for projects and representatives
- ✅ Static data integration for initial testing

### Phase 2: Core Feature Enhancement (COMPLETED)
- ✅ Entity status management system
- ✅ Project-jurisdiction associations
- ✅ Status distribution visualizations
- ✅ Entity statuses can be updated

### Phase 3: Database Integration (COMPLETED)
- ✅ Design database abstraction layer to support multiple providers
- ✅ Implement SQLite adapter for local development
- ✅ Create SQLAlchemy models matching validated data structure
- ✅ Build dependency injection system for database providers

### Phase 4: Improve DB Filters and Status Display (COMPLETED)
- ✅ Improve DB filtering. 
- ✅ Ensure status are only displayed for in district entities
- ✅ Ensure that all entities are counted as providing a status (even if no status exists)
- ✅ Ensure status updates updates status display. 
- ✅ Display status counts along with colored distribution

### Phase 5: Ensure Entities/Project have Correct Data and Display Correctly (COMPLETED)
- ✅ Add district to entity
- ✅ Ensure entity contact info is saved correctly and displayed
- ✅ Clean up display of entity list (should be more compact)
- ✅ Clean up display of project list

### Phase 6: Get Better Example Data and Allow Creating/Editing Projects (COMPLETED)
- ✅ Pull in real data for Chicago alders
- ✅ Ensure that creating/editing a project works as intended
- ✅ Improve project create/edit form styling
- ✅ Setup proper project status filtering (it was bugged before)
- ✅ Hide archived projects by default

### Phase 7: Location Module Proof of Concept (PLANNED)
- Ensure that location properly links up to jurisdictions/entities (can potentially consolidate)
- Create a minimal Chicago module that demonstrates the pluggable concept
- Test switching between "default" and "Chicago" modules
- Get real address lookup working (need to get geojson for Chicago wards)

### Phase 8: Validate Postgres Provider Works as Intended (PLANNED)
- Setup postgres locally
- Test all workflows with a postgres and ensure things work

### Phase 9: Add Auth/Admin System (PLANNED)
- Add authentication and roles system
- Segment projects by group
- Allow groups to hide some/all projects
- Make projects shareable

### Phase 10: Cleanup Existing Implementation (PLANNED)
- Don't reload entire project list on status/search text change
- Replace various magic strings with enums
- Clean up data models (remove any unnecessary optionals or List/Dict)
- Clean up logic fetching status/jurisdiction for projects (it is duplicated across a couple endpoints)
- Add some basic frontend/backend tests
- Add some core tests to help validate that ensure future changes don't break anything
- At least a few integration tests.
- Ensure string filtering is done on the backend (atm, I am just filtering on the frontend)

## 5. Features To Eventually Add
- Create an entity detail page that display entity info + associated projects/status
- Ability to update/display a project timeline and current status (bill timeline)
- Display of user's representatives and where they stand on specific issues (entity X opposes project Y)
- Setup "Contact your Rep about this Project" workflow
- Make entity metadata more flexible. Allowing adding arbitrary contact fields or other data.
- Add IL House/Senate jurisdictions
- Create add entity page?
- Create add jurisdiction pages?


## 6. Next Steps After Validation

Potential next steps (with rough prioritization)

1. Complete Illinois specific location module
2. Authentication and authorization system
3. Additional UI polish
4. Template response generation
5. Deployment infrastructure
6. Containerize things

