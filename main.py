from fastapi import FastAPI ,status
from db.config import engine, Base

app = FastAPI(title="Asset Allocation System")

@app.get("/",status_code=status.HTTP_200_OK)
def root():
    return { "status_code" :status.HTTP_200_OK ,"message": "Welcome to Asset Allocation System API"}
