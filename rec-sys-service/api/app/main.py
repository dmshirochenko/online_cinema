from fastapi import FastAPI
from .routers.v1 import rec as rec_v1

app = FastAPI()

app.include_router(rec_v1.router)
