# To connect to venv use command:
# source venv/bin/activate

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import projects, tickets, users, auth, comments
# Modules needed for creating tables through sqlqlchemy; Drop if using alembic
# from . import models
# from .database import engine

# Set domains that are able to access this API
# Origins is a white-list for domains
origins = []
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(projects.router)
app.include_router(tickets.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(comments.router)

# Create tables using sqlalchemy; Drop it if you use alembic
# models.Base.metadata.create_all(bind=engine)

# Test message
@app.get("/")
def test_message():
    return {"message": "successfully deployed from CI/CD pipeline"}







    
