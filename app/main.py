from fastapi import FastAPI, status

from app.db import models as models
from app.db.database import engine
from app.routers import admin, auth, todos, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
