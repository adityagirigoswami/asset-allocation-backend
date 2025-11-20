from fastapi import FastAPI, status, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from api.routes.auth_routes import router as auth_router
from api.routes.admin_routes import (router as admin_router, employees_router as employees_admin_router)
from api.routes.asset_category_routes import router as category_router
from api.routes.asset_routes import (router as asset_router, dashboard_router as dashboard_router)
from api.routes.allocation_routes import (router as allocation_router, employees_router as employees_allocation_router)
from api.routes.return_request_routes import (router as rr_router, employees_router as employees_return_request_router)
from core.cors import setup_cors
from core.exceptions import create_error_response

app = FastAPI(title="Asset Allocation System")

setup_cors(app)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and return standardized error response"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.status_code, str(exc.detail))
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return standardized error response"""
    errors = exc.errors()
    error_messages = []
    
    # Map common validation error types to user-friendly messages
    error_type_messages = {
        "missing": "is required",
        "value_error": "has invalid value",
        "type_error": "has wrong type",
        "string_too_short": "is too short",
        "string_too_long": "is too long",
        "greater_than": "must be greater",
        "less_than": "must be less",
    }
    
    for error in errors:
        # Get field path (skip 'body' prefix for cleaner messages)
        loc = error.get("loc", [])
        field_path = [str(loc_item) for loc_item in loc if loc_item != "body"]
        field_name = " -> ".join(field_path) if field_path else "input"
        
        # Get error type and message
        error_type = error.get("type", "")
        msg = error.get("msg", "Invalid value")
        
        # Create user-friendly message
        if error_type in error_type_messages:
            friendly_msg = f"{field_name} {error_type_messages[error_type]}"
        else:
            # Use the original message but make it more readable
            friendly_msg = f"{field_name}: {msg}"
        
        error_messages.append(friendly_msg)
    
    # Combine error messages
    if len(error_messages) == 1:
        error_message = error_messages[0]
    else:
        error_message = "Check: " + "; ".join(error_messages)
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(422, error_message)
    )

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(category_router)
app.include_router(asset_router)
app.include_router(dashboard_router)
app.include_router(employees_admin_router)
app.include_router(allocation_router)
app.include_router(employees_allocation_router)
app.include_router(rr_router)
app.include_router(employees_return_request_router)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Welcome to Asset Allocation System API",
    }

@app.get("/reset-password")
def reset_password_preview(token: str):
    return {"message": "Use this token to call /auth/password/reset", "token": token}
