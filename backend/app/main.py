from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, groups, entities, status, jurisdictions, location
from app.utils.data_loader import load_data_into_provider
from app.models.pydantic.models import (
    Project,
    Group,
    Entity,
    Jurisdiction,
    EntityStatusRecord,
)
from app.db.dependencies import (
    project_provider,
    group_provider,
    entity_provider,
    jurisdictions_provider,
    status_records_provider,
)
import os
import logging
import time
from fastapi import Request


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("open-advocacy")

app = FastAPI(
    title="Open Advocacy API",
    description="API for connecting citizens with representatives and tracking advocacy projects",
    version="0.1.0",
)

# Add CORS middleware for development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite dev server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get client IP and request details
    client_host = request.client.host if request.client else "unknown"

    logger.info(
        f"Request started: {request.method} {request.url.path} from {client_host}"
    )

    try:
        response = await call_next(request)

        # Calculate request processing time
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        return response
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path} - Error: {str(e)}"
        )
        raise


@app.get("/")
async def root():
    return {"message": "Welcome to Open Advocacy API"}


app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(status.router, prefix="/api/status", tags=["status"])
app.include_router(
    jurisdictions.router, prefix="/api/jurisdictions", tags=["jurisdictions"]
)
app.include_router(location.router, prefix="/api/location", tags=["location"])


@app.on_event("startup")
async def startup_event():
    """Load sample data on startup."""
    # Get the project root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load projects data
    projects_file = os.path.join(project_dir, "data", "dummy_projects.json")
    if os.path.exists(projects_file):
        await load_data_into_provider(project_provider, Project, projects_file)

    # Load other sample data files if they exist
    groups_file = os.path.join(project_dir, "data", "dummy_groups.json")
    if os.path.exists(groups_file):
        await load_data_into_provider(group_provider, Group, groups_file)

    entities_file = os.path.join(project_dir, "data", "dummy_entities.json")
    if os.path.exists(entities_file):
        await load_data_into_provider(entity_provider, Entity, entities_file)

    jurisdictions_file = os.path.join(project_dir, "data", "dummy_jurisdictions.json")
    if os.path.exists(jurisdictions_file):
        await load_data_into_provider(
            jurisdictions_provider, Jurisdiction, jurisdictions_file
        )

    status_records_file = os.path.join(project_dir, "data", "dummy_status_records.json")
    if os.path.exists(status_records_file):
        await load_data_into_provider(
            status_records_provider, EntityStatusRecord, status_records_file
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
