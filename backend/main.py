from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Organizational Memory Engine")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running"}