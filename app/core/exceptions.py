from fastapi import Request, status
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
            else:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "detail": "A record with this unique identifier already exists."
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected database error occurred"},
        )
