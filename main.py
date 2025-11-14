from fastapi import FastAPI
from db.config import engine, Base

app = FastAPI(title="Asset Allocation System")

@app.get("/")
def root():
    return {"message": "Welcome to Asset Allocation System API"}
