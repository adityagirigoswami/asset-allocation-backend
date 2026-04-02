"""Common exception handling and error messages"""
from fastapi import HTTPException, status
from typing import Optional


# User-friendly error messages mapped to status codes
ERROR_MESSAGES = {
    400: "Invalid request. Please check your input.",
    401: "Unauthorized. Please log in with valid credentials.",
    403: "Access denied. You don't have permission for this action.",
    404: "Resource not found. Please check the ID and try again.",
    409: "Resource already exists. Please use a different value.",
    422: "Invalid data. Please check all required fields.",
    500: "Server error. Please try again later.",
}


def get_user_friendly_message(status_code: int, custom_message: Optional[str] = None) -> str:
    """
    Get user-friendly error message based on status code.
    
    Args:
        status_code: HTTP status code
        custom_message: Optional custom message to use instead of default
    
    Returns:
        User-friendly error message
    """
    if custom_message:
        return custom_message
    
    # Map specific status codes to user-friendly messages
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "Unauthorized. Please log in again."
    elif status_code == status.HTTP_403_FORBIDDEN:
        return "Access denied. Insufficient permissions."
    elif status_code == status.HTTP_404_NOT_FOUND:
        return "Resource not found. Please verify and try again."
    elif status_code == status.HTTP_409_CONFLICT:
        return "Resource already exists. Use a different value."
    elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return "Invalid data. Check all fields and try again."
    elif status_code == status.HTTP_400_BAD_REQUEST:
        return "Invalid request. Please check your input."
    
    # Default message based on status code range
    return ERROR_MESSAGES.get(status_code, f"Error occurred. Please try again.")


def create_error_response(
    status_code: int,
    custom_message: Optional[str] = None,
    field_name: Optional[str] = None
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        custom_message: Optional custom error message
        field_name: Optional field name for validation errors
    
    Returns:
        Standardized error response dictionary
    """
    message = get_user_friendly_message(status_code, custom_message)
    
    # Add field-specific context for validation errors
    if field_name and status_code == 422:
        message = f"'{field_name}' is invalid. {message}"
    
    return {
        "status_code": status_code,
        "error": message,
        "success": False
    }


class AppHTTPException(HTTPException):
    """Custom HTTPException with standardized error format"""
    
    def __init__(
        self,
        status_code: int,
        custom_message: Optional[str] = None,
        field_name: Optional[str] = None
    ):
        error_response = create_error_response(status_code, custom_message, field_name)
        super().__init__(
            status_code=status_code,
            detail=error_response["error"]
        )
        self.error_response = error_response

