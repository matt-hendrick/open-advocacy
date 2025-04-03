from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import projects, location
from app.utils.data_loader import load_data_into_provider
from app.models.pydantic.models import Project
from app.db.dependencies import project_provider
import os


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


@app.get("/")
async def root():
    return {"message": "Welcome to Open Advocacy API"}


app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(location.router, prefix="/api/location", tags=["location"])


@app.on_event("startup")
async def startup_event():
    """Load sample data on startup."""
    # Get the project root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load projects data
    projects_file = os.path.join(project_dir, "data", "dummy_projects.json")
    await load_data_into_provider(project_provider, Project, projects_file)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
