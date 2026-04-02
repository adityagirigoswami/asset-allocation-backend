"""Helper functions for raising standardized errors in routes"""
from fastapi import HTTPException, status
from core.exceptions import create_error_response


def raise_error(status_code: int, custom_message: str = None):
    """
    Raise an HTTPException with standardized error format.
    
    This is a convenience function for routes to use when they want to
    raise errors with custom messages that will be automatically formatted.
    
    Args:
        status_code: HTTP status code
        custom_message: Custom error message (optional)
    
    Example:
        raise_error(404, "Asset with ID 123 not found")
        raise_error(401)  # Uses default message for 401
    """
    error_response = create_error_response(status_code, custom_message)
    raise HTTPException(
        status_code=status_code,
        detail=error_response["error"]
    )


def raise_not_found(resource_name: str = "Resource", identifier: str = None):
    """Raise a 404 error with a user-friendly message"""
    if identifier:
        message = f"{resource_name} '{identifier}' not found."
    else:
        message = f"{resource_name} not found."
    raise_error(status.HTTP_404_NOT_FOUND, message)


def raise_unauthorized(message: str = None):
    """Raise a 401 error with a user-friendly message"""
    if not message:
        message = "Unauthorized. Please log in again."
    raise_error(status.HTTP_401_UNAUTHORIZED, message)


def raise_forbidden(message: str = None):
    """Raise a 403 error with a user-friendly message"""
    if not message:
        message = "Access denied. Insufficient permissions."
    raise_error(status.HTTP_403_FORBIDDEN, message)


def raise_conflict(resource_name: str = "Resource", field_name: str = None):
    """Raise a 409 error for conflicts (e.g., duplicate values)"""
    if field_name:
        message = f"{resource_name} with this {field_name} already exists."
    else:
        message = f"{resource_name} already exists."
    raise_error(status.HTTP_409_CONFLICT, message)


def raise_bad_request(message: str):
    """Raise a 400 error with a custom message"""
    raise_error(status.HTTP_400_BAD_REQUEST, message)

