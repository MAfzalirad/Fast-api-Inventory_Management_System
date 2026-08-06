from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers import admin, auth, items
import app.models as models
from app.database import engine
from app.routers import users

app = FastAPI(title="Inventory Management API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials= False,
    allow_methods=['*'],
    allow_headers=['*'],
)


models.Base.metadata.create_all(bind=engine)


app.include_router(items.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)