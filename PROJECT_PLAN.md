# Open Advocacy Implementation Plan - FastAPI + React TypeScript Approach

## 1. Project Overview

Open Advocacy is an open-source platform connecting citizens with representatives and tracking advocacy projects. This plan outlines our FastAPI backend with a flexible database layer and React+TypeScript+Vite frontend.

## 2. Current Implementation Status

- ✅ **Backend**: FastAPI application with Pydantic models and in-memory storage
- ✅ **Frontend**: React+TypeScript+Vite application with UI components
- ✅ **Core Components**: Project listing and representative lookup functionality
- ✅ **Data Flow**: Initial implementation of frontend-backend connection
- ✅ **Database**: Setup flexible database provider system that supports Sqlite or postgres
- ✅ **Representative Lookup Feature**: Users can enter in their address to lookup who their representatives are
- ⏳ **Replicable Deployment Process Setup**: Pending
- ⏳ **Auth and Admin User Features**: Functionality pending


## 3. Core Concepts & Data Model

### Projects
- **Core Properties**: title, description, status, link field
- **Relationships**: Associated with one or many jurisdictions
- **Status Preferences**: Each project has a preferred status goal for entities
- **Template Responses**: Can include template advocacy language
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
- ✅ Updating entity status does not update the status for the entity properly on the project detail page

### Phase 7: Location Module Proof of Concept (COMPLETED)
- ✅ Get geojson for Chicago wards
- ✅ Get real address lookup working 
- ✅ Re-evaluate Location feature. It may make more sense to allow a user to input an address and show them all districts they fall within (along with entities associated with those). User enters address, we look up their coordinates, optionally filter by jurisdiction, and then use SQL geography to see if their point is within a geojson line. If not filtering by jurisdiction, return all.
- ✅ Ensure that location properly links up to jurisdictions/entities (can potentially consolidate)

### Phase 8: Improve Representative Lookup and Displaying Entity Information to the User (COMPLETED)
- ✅ Improve the styling of the lookup representatives page
- ✅ Save user's representative data to local storage
- ✅ Clean up massive monolothic RepresenativeLookup.tsx. It is messy and has a bunch of things that should be their own files.
- ✅ Use that entity data to highlight where their rep stands on the project detail page (for a project in which their rep is in the jurisdiction)
- ✅ Add an entity detail page that displays the entities info and their stance on projects they are linked to
- ✅ Fix rep search input width (it is too small)
- ✅ Improve styling of buttons linking to entity detail page
- ✅ Make entity name on rep lookup page a link and make project name on entity detail page a link.

### Phase 9: Validate Postgres Provider Works as Intended (Completed)
- ✅ Setup postgres locally
- ✅Test all workflows with a postgres and ensure things work end-to-end

### Phase 10: Determine Deployment Steps for MVP (COMPLETED)
- ✅ Investigate deployment options (want something cheap, quick, and easy to maintain)
- ✅ Where do I want to deploy this? - Update: Railway for an MVP
- ✅ How do I want to manage deployments (terraform?)?
- ✅ Document a plan for deployment

### Phase 11: Actually Deploy this Somewhere (COMPLETED)
- ✅ Deploy the app according to whatever is determined in the previous step

### Phase 12: Test and Document Deployment (COMPLETED)
- ✅ Test all workflows on the deployed version of the application
- ✅ Document the current state of the application.
- ✅ Clean up existing readmes
- ✅ Test running the application fresh on another machine to validate instructions are correct

### Phase 13: Add Script to Add in IL Data, Fix Bugs, and add in Service Layer (COMPLETED)
- ✅ Add script to add IL House/Senate data
- ✅ Fix a bug with project creation
- ✅ Create a service layer between routes and the DB logic

### Phase 14: Build a flexible, cleaner import system (IN PROGRESS)
- ✅ Build an extensible import system
- ✅ Clean up and consolidate various utility scripts
- ✅ Fix duplicated districts import bug
- ✅ Add optional image url to entities and display on the frontend

### Phase 15: Add Auth/User/Admin System (PLANNED)
- Add authentication and roles system
- Add an in UI means of adding Chicago/IL data for users with the permissions
- Segment projects by group
- Allow groups to hide some/all projects
- Make projects shareable

### Phase 16: Better Bulk Data Management/Import (PLANNED)
- Investigate exporting/import project data
- Allow editing many statuses at once

### Phase 17: Cleanup Existing Implementation (PLANNED)
- Fix all the frontend typing/linting errors
- Rename frontend components with Representatives to Entities to be more generic
- Clean up various frontend components that could be further broken up (ex: Header.tsx, UserEntityProjectSection.tsx). 
- Don't reload entire project list on status/search text change
- Ensure all backend endpoints use DB filter methods (don't use .list)
- Everything is UTC atm, reconsider that
- Replace various magic strings with enums
- Clean up data models (remove any unnecessary optionals or List/Dict)
- Clean up logic fetching status/jurisdiction for projects (it is duplicated across a couple endpoints)
- Clean up random console logs and prints
- Add some basic frontend/backend tests
- Add some core tests to help validate that ensure future changes don't break anything
- At least a few integration tests.
- Ensure string filtering is done on the backend (atm, I am just filtering on the frontend)

## 5. Features To Eventually Add
- Ability to update/display a project timeline and current status (project/bill timeline)
- Setup "Contact your Rep about this Project" workflow
- Make entity metadata more flexible. Allowing adding arbitrary contact fields or other data.
- Create add entity page?
- Create add jurisdiction pages?