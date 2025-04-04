# Open Advocacy Implementation Plan - FastAPI + React TypeScript Approach

## 1. Project Overview

Open Advocacy is an open-source platform connecting citizens with representatives and tracking advocacy projects. This plan outlines our FastAPI backend with a flexible database layer and React+TypeScript+Vite frontend.

## 2. Current Implementation Status

- ✅ **Backend**: FastAPI application with Pydantic models and in-memory storage
- ✅ **Frontend**: React+TypeScript+Vite application with UI components
- ✅ **Core Components**: Project listing and representative lookup functionality
- ✅ **Data Flow**: Initial implementation of frontend-backend connection
- ⏳ **Database**: Still using in-memory storage (SQLite integration pending)
- ⏳ **Admin Features**: Basic structure created, functionality pending

## 3. Core Concepts & Data Model

### Projects
- **Core Properties**: title, description, status, link field
- **Relationships**: Associated with one or many jurisdictions
- **Status Preferences**: Each project has a preferred status goal for entities
- **Template Responses**: Can include template advocacy language (future feature)
- **Vote Aggregation**: Display color-coded distribution of entity positions

### Entity Status Types
- **Five Default Status Types**:
  - Solid Approval (Strong Support)
  - Leaning Approval (Tentative Support)
  - Neutral (Undecided/Unknown)
  - Leaning Disapproval (Tentative Opposition)
  - Solid Disapproval (Strong Opposition)
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

### Phase 2: Core Feature Enhancement (IN PROGRESS)
- ✅ Entity status management system
- ✅ Project-jurisdiction associations
- ✅ Status distribution visualizations
- ✅ Admin interfaces for status updates

### Phase 3: Database Integration (PLANNED)
- Design database abstraction layer to support multiple providers
- Implement SQLite adapter for local development
- Create SQLAlchemy models matching validated data structure
- Build dependency injection system for database providers

### Phase 4: Location Module Proof of Concept (PLANNED)
- Create a minimal Chicago module that demonstrates the pluggable concept
- Use a small static dataset of Chicago wards and representatives
- Test switching between "default" and "Chicago" modules

### Phase 5: Cleanup Existing Implementation (PLANNED)
- Add district to entity
- Ensure status distribution visualizations always reflect entities displayed
- Add some basic frontend/backend tests

## 5. MVB Implementation Steps

1. **Update Data Models** (Next Step)
   - Add jurisdictions field to projects
   - Create entity status records model
   - Link entities to jurisdictions

2. **Implement Status Management**
   - Create admin interface for updating entity statuses
   - Build status distribution visualizations
   - Add color-coding for status indicators

3. **Enhance Project Views**
   - Show jurisdiction associations
   - Display status distribution charts
   - Add filtering by jurisdiction

4. **Build Admin Features**
   - Admin-only routes for status updates
   - Project management interfaces
   - Status history tracking

5. **Implement Database Storage**
   - Move from in-memory to SQLite
   - Create database migration system
   - Implement proper joins for related data

## 8. Next Steps After Validation

Potential next steps (with rough prioritization)

1. Complete Chicago/Illinois specific location module
2. Authentication and authorization system
3. Entity-specific notes functionality
4. Additional UI polish
5. Template response generation
6. Deployment infrastructure

