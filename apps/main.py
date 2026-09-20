import os  # CI失敗確認用の未使用import(直後にrevertする)
from fastapi import FastAPI

from apps.routers import add, divide, multiply, subtract

app = FastAPI(title="Calculator API")

app.include_router(add.router)
app.include_router(subtract.router)
app.include_router(multiply.router)
app.include_router(divide.router)
