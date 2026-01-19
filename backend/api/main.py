"""
FastAPI main application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import resume, ai, applications, pdf

app = FastAPI(
    title="Resume Helper API",
    description="API for Resume Helper application",
    version="1.0.0"
)

# CORS middleware - configure appropriately for your deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router)
app.include_router(ai.router)
app.include_router(applications.router)
app.include_router(pdf.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Resume Helper API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

