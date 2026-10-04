from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from backend.domain.errors import CaseNotFoundError, DocumentParseError


def problem(status: int, title: str, detail: str, instance: str, trace_id: str | None = None):
    return JSONResponse(status_code=status, media_type="application/problem+json",
                        content={"type": "about:blank", "title": title, "status": status,
                                 "detail": detail, "instance": instance, "trace_id": trace_id})


def install_error_handlers(app: FastAPI):
    @app.exception_handler(CaseNotFoundError)
    async def not_found(request: Request, exc: CaseNotFoundError):
        return problem(404, "Case not found", "The requested case is not present in the supplied manifest.", str(request.url.path))

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        return problem(422, "Request validation failed", "The request does not match the expected schema.", str(request.url.path))

    @app.exception_handler(DocumentParseError)
    async def parse_error(request: Request, exc: DocumentParseError):
        return problem(422, "Document could not be read", str(exc), str(request.url.path))

    @app.exception_handler(Exception)
    async def internal(request: Request, exc: Exception):
        trace = uuid4().hex
        return problem(500, "Internal processing error", "The review could not be completed. See trace_id for support.", str(request.url.path), trace)
