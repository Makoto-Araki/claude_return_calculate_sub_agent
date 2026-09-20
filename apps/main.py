from fastapi import FastAPI

from apps.routers import add

app = FastAPI(title="Calculator API")

app.include_router(add.router)
