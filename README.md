# Open Advocacy

Open Advocacy is an open-source web application connecting citizens with representatives and tracking advocacy projects. The web application allows users to look up their representatives, track advocacy projects, and understand where representatives stand on various issues.

## Current Project Features

- **Project Tracking**: View active advocacy projects with details on their status
- **Representative Lookup**: Find your representatives by entering your address
- **Status Visualization**: See color-coded representations of where representatives stand on issues
- **Geographic Integration**: Utilizes geospatial data to accurately match addresses to districts (if the geojson data has been imported into the DB)
- **Authentication & User Management**: Role-based access control with user registration, login, and admin functionality

## Tech Stack

- **Backend**: FastAPI with SQLAlchemy ORM and Pydantic models
- **Frontend**: React with TypeScript and Vite
- **Database**: Flexible database layer supporting SQLite (for development) and PostgreSQL (for production)
- **Containerization**: Docker and Docker Compose for easy deployment

## Data Model

The application uses the following core concepts:

- **Projects**: Advocacy initiatives that can be tracked and monitored
- **Entities**: Representatives or officials who have a position on projects
- **Jurisdictions**: Legislative bodies (e.g., City Council, State Senate)
- **Districts**: Geographic areas represented by entities
- **Status Records**: Track where entities stand on specific projects
- **Users & Groups**: User management with role-based permissions (Super Admin, Group Admin, Editor, Public)

## User Roles & Permissions

- **Public**: Can view projects, lookup representatives, see status distributions
- **Editors**: Can create/edit projects and update entity statuses
- **Group Admins**: Can manage users within their group and have editor permissions
- **Super Admins**: Full system access including user management across all groups

## Backend Architecture

- **API Layer**: FastAPI routes that handle HTTP requests and responses
- **Service Layer**: Business logic organized by domain entities
- **Data Access Layer**: Abstract database providers with concrete implementations
- **Authentication Layer**: JWT-based auth with role-based access control
- **Geo Services**: Specialized geographic functionality
- **Models**: Pydantic models for validation and ORM models for persistence

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose for the simplest setup
- Alternatively for local development:
  - Python 3.9+ with [Poetry](https://python-poetry.org/docs/)
  - Node.js 16+ with npm

### Running the Application with Docker Compose

The easiest way to get started is using Docker Compose, which will run frontend, backend, and postgres containers:

```bash
docker-compose up
```
Once running, you can access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Setting Up Example Data

To populate the database with example data, follow these steps:

1. Navigate to the backend directory:
  ```bash
  cd backend
  ```

2. Activate the Poetry shell:
  ```bash
  poetry shell
  ```

3. Create necessary database tables
  ```bash
  python -m scripts.init_db
  ```

4. Load Chicago City Council data:
  ```bash
  python -m scripts.import_data chicago
  ```

5. Import Illinois House and Senate representative data:
  ```bash
  python -m scripts.import_data illinois
  ```

6. Create a super admin user (required for accessing admin features):
  ```bash  
  python -m scripts.add_super_admin
  ```

## Project Structure
```
open-advocacy/
├── backend/                     # FastAPI backend service
│   ├── app/                     # Application code
│   │   ├── api/                 # API endpoints
│   │   │   └── routes/          # API route handlers
│   │   │       ├── admin/       # Admin-specific routes
│   │   │       │   ├── imports.py
│   │   │       │   └── users.py
│   │   │       ├── auth.py      # Authentication routes
│   │   │       ├── entities.py  # Entity management routes
│   │   │       ├── groups.py    # Group management routes
│   │   │       ├── jurisdictions.py
│   │   │       ├── projects.py  # Project management routes
│   │   │       └── status.py    # Status tracking routes
│   │   ├── core/                # Core configuration
│   │   │   ├── auth.py          # Authentication utilities
│   │   │   └── config.py        # Application configuration
│   │   ├── db/                  # Database utilities
│   │   ├── geo/                 # Geospatial utilities
│   │   ├── imports/             # Import system
│   │   ├── models/              # Data models
│   │   │   ├── orm/             # SQLAlchemy ORM models
│   │   │   └── pydantic/        # Pydantic validation models
│   │   └── services/            # Business logic services
│   │       ├── entity_service.py
│   │       ├── group_service.py
│   │       ├── project_service.py
│   │       ├── status_service.py
│   │       ├── user_service.py
│   │       └── service_factory.py
│   ├── data/                    # Database and geospatial data
│   └── scripts/                 # Setup and maintenance scripts
│       ├── add_super_admin.py   # Create super admin user
│       ├── import_data.py       # Data import utilities
│       └── init_db.py           # Database initialization
├── frontend/                    # React+TypeScript frontend
│   ├── public/                  # Static assets
│   └── src/                     # Application source code
│       ├── components/          # Reusable UI components
│       │   ├── auth/            # Authentication components
│       │   │   ├── ConditionalUI.tsx    # Role-based UI rendering
│       │   │   └── ProtectedRoute.tsx   # Route protection
│       │   ├── common/          # Common UI components
│       │   ├── Entity/          # Entity-specific components
│       │   ├── Group/           # Group management components
│       │   ├── Project/         # Project-specific components
│       │   └── Status/          # Status visualization components
│       ├── contexts/            # React contexts
│       │   ├── AuthContext.tsx  # Authentication state management
│       │   └── UserRepresentativesContext.tsx
│       ├── hooks/               # Custom React hooks
│       ├── pages/               # Page components
│       │   ├── admin/           # Admin-specific pages
│       │   │   ├── RegisterPage.tsx     # User registration
│       │   │   └── UserManagementPage.tsx # User management
│       │   ├── EntityDetail.tsx
│       │   ├── HomePage.tsx
│       │   ├── LoginPage.tsx    # User login
│       │   ├── ProjectDetail.tsx
│       │   ├── ProjectList.tsx
│       │   └── RepresentativeLookup.tsx
│       ├── services/            # API services
│       │   ├── api.ts           # Base API configuration
│       │   ├── auth.ts          # Authentication API calls
│       │   ├── user.ts          # User management API calls
│       │   └── ...              # Other service files
│       ├── types/               # TypeScript type definitions
│       └── utils/               # Utility functions
└── docker-compose.yaml          # Docker Compose configuration
```

## Configuration

The application can be configured through environment variables. The primary configurations are:

- `DATABASE_PROVIDER`: Database backend to use (`sqlite` or `postgres`)
- `DATABASE_URL`: Connection string for the database
- `AUTH_SECRET_KEY`: Secret key for JWT token generation

See `backend/app/core/config.py` for all available configuration options.

## Development Status
This project is currently in active development. The implementation plan in PROJECT_PLAN.md tracks completed and upcoming features.
Currently completed:

- ✅ Core backend and frontend implementation
- ✅ Project and representative lookup functionality
- ✅ Database integration with SQLite and PostgreSQL support
- ✅ Representative lookup with geographic data integration using Nominatim/OpenStreetMap
- ✅ Authentication, user management, and role-based access control system

Planned additional work:

- Improved bulk data management and import/export functionality via admin ui
- Better project segmentation and sharing capabilities
- Enhanced mobile styling and user experience
- Test coverage
- General code cleanup and optimization

## Screenshots

### Project List Page
![Project List Page](./screenshots/project_list.png)

### Project Page
![Project Page](./screenshots/project.png)

### Find Your Representatives Page
![Find Your Representatives Page](./screenshots/find_your_representatives.png)

### Representatives Page
![Representative Page](./screenshots/representative.png)


## Contributing

Contributions are welcome! If you're interested in contributing, please:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request

## License

This project is licensed under the MIT License