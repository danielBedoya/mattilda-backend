from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def register_exception_handlers(app):
    """
    Registers custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        Handles SQLAlchemy IntegrityError exceptions, providing specific error messages
        for duplicate key violations.
        """
        if "duplicate key value violates unique constraint" in str(exc.orig):
            if "students_email_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": "Student with this email already exists"},
                )
            elif "students_document_number_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "detail": "Student with this document number already exists"
                    },
                )
            elif "users_username_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": "Username already registered"},
                )
            elif "users_email_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": "Email already registered"},
                )
            elif "schools_name_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": "School with this name already exists"},
                )
            elif "document_types_name_key" in str(exc.orig):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"detail": "Document type with this name already exists"},
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "detail": "A record with this unique identifier already exists."
                    },
                )
        elif "violates foreign key constraint" in str(exc.orig):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Related record not found or invalid reference."},
            )
        elif "violates not-null constraint" in str(exc.orig):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "A required field is missing or null."},
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected database error occurred"},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handles FastAPI HTTPException, returning a JSON response."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
