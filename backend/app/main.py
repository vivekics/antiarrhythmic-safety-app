from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .database import engine, Base, SessionLocal
from .models import User
from .auth import get_password_hash
from .routers import auth, patients


def create_tables():
    Base.metadata.create_all(bind=engine)


def create_default_admin():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("Default admin user created → username: admin / password: admin123")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    create_default_admin()
    yield


app = FastAPI(
    title="Antiarrhythmic Medication Safety API",
    description="Cloud-based safety assessment for synthetic clinical profiles",
    version="1.0.0",
    lifespan=lifespan
)

# CORS – allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)


@app.get("/")
def root():
    return {
        "message": "Antiarrhythmic Medication Safety API",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
