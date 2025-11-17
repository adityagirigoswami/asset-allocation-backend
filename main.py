from fastapi import FastAPI , status
from api.routes.auth_routes import router as auth_router
from api.routes.admin_routes import router as admin_router
from api.routes.asset_category_routes import router as category_router
from api.routes.asset_routes import router as asset_router
from api.routes.allocation_routes import router as allocation_router
from api.routes.return_request_routes import router as rr_router
app = FastAPI(title="Asset Allocation System")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(category_router)
app.include_router(asset_router)
app.include_router(allocation_router)
app.include_router(rr_router)


@app.get("/",status_code=status.HTTP_200_OK)
def root():
    return { "status_code" :status.HTTP_200_OK ,"message": "Welcome to Asset Allocation System API"}
