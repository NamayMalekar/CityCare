"""
CityCare Clinic — FastAPI entry point. Multi-Hospital System with RBAC.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, clinic, appointment, doctor, super_admin, hospital_admin, patient

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
)
logger = logging.getLogger("citycare")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="CityCare Multi-Hospital Platform API",
    description="Multi-Hospital System with Role-Based Access Control (RBAC)",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Error armour ─────────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """Join field-by-field complaints into one clean line for the UI banner."""
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"] if p not in ("body",))
        parts.append(f"{loc}: {err['msg']}" if loc else err["msg"])
    detail = " | ".join(parts) if parts else "Invalid request."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail},
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Something went wrong on our side. Please try again."},
    )


# ── Wire up all routes (both with and without /api prefix) ────────────────────
routers = [
    auth.router,
    clinic.router,
    appointment.router,
    doctor.router,
    super_admin.router,
    hospital_admin.router,
    patient.router,
]

for r in routers:
    app.include_router(r)
    app.include_router(r, prefix="/api")


@app.get("/api/health", tags=["health"])
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "CityCare Multi-Hospital API"}


# ── Serve Frontend SPA ───────────────────────────────────────────────────────
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "citycare-frontend", "dist")
)

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str):
        # Don't hijack API routes
        api_prefixes = (
            "api/", "docs", "openapi.json", "auth/", "clinic/", "appointments/",
            "doctor/", "super-admin/", "hospital-admin/", "patient/"
        )
        if any(full_path.startswith(prefix) for prefix in api_prefixes):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)

        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)

        return JSONResponse(status_code=404, content={"detail": "Frontend index.html not found."})
