from fastapi import FastAPI
import models
from database import engine
from routers import items, auth, users, admin

app = FastAPI(title="Inventory Management API")

models.Base.metadata.create_all(bind=engine)

app.include_router(items.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)