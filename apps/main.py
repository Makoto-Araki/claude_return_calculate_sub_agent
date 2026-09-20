from fastapi import FastAPI

from apps.routers import add, subtract

app = FastAPI(title="Calculator API")

app.include_router(add.router)
app.include_router(subtract.router)
