from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, groups, entities, status, jurisdictions
import logging
import time

from app.core.config import settings
from app.db.session import create_tables, init_postgis

from app.scripts.chicago_city_council_setup import setup_chicago_city_council_data
from app.scripts.import_chicago_ward_geojson import import_chicago_wards
from app.db.dependencies import get_jurisdictions_provider, get_districts_provider
from app.models.pydantic.models import DistrictBase, Jurisdiction



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
    root_path="/",
)

# Add CORS middleware for development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite dev server port
]

if settings.ALLOWED_ORIGIN:
    origins.append(settings.ALLOWED_ORIGIN)

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


# TODO: Remove this
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


# TODO: Consider if this is necessary
@app.on_event("startup")
async def startup_event():
    """Initialize database and load sample data on startup."""
    logger.info(
        f"Starting application with {settings.DATABASE_PROVIDER} database provider"
    )
    # await create_tables()
    jurisdiction_list = None
    try:
        jurisdictions_provider = get_jurisdictions_provider()
        jurisdiction_list: list[Jurisdiction] = await jurisdictions_provider.filter(
                name="Chicago City Council"
            )
    except Exception:
        logger.exception("There was an error fetching jurisdictions.")
    
    if not jurisdiction_list or len(jurisdiction_list) < 1:
        logger.info("Filling database with Chicago city council data")

        await init_postgis()

        await setup_chicago_city_council_data()

        await import_chicago_wards()



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
