from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Database
from app.routers import auth, documents, organizations, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await Database.connect_db()
    yield
    # Shutdown
    await Database.close_db()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(
    organizations.router, prefix=f"{settings.API_PREFIX}/orgs", tags=["organizations"]
)
app.include_router(
    templates.router,
    prefix=f"{settings.API_PREFIX}/orgs/{{org_id}}/templates",
    tags=["templates"],
)
app.include_router(
    documents.router,
    prefix=f"{settings.API_PREFIX}/orgs/{{org_id}}/docs",
    tags=["documents"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Document Composition Platform API",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
