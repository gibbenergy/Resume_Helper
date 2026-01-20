"""
FastAPI main application entry point.
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.routers import resume, ai, applications, pdf

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Helper API",
    description="API for Resume Helper application",
    version="1.0.0"
)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging."""
    logger.error(f"Validation error on {request.method} {request.url.path}")
    logger.error(f"Validation details: {exc.errors()}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# CORS middleware - configure appropriately for your deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

