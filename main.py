from fastapi import FastAPI , status
from api.routes.auth_routes import router as auth_router

app = FastAPI(title="Asset Allocation System")

app.include_router(auth_router)

@app.get("/",status_code=status.HTTP_200_OK)
def root():
    return { "status_code" :status.HTTP_200_OK ,"message": "Welcome to Asset Allocation System API"}
