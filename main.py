from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import auth, users, routes
from db.database import engine, Base
import os


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vision Classifier API",
    description="Asynchronous AI-powered image classification system.",
    version="1.0.0"
)

cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
allow_all_origins = cors_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(routes.router)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "Vision Classifier API is working! Go to /docs for Swagger UI."}