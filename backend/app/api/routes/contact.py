"""
GrowFlow — Public Contact Inquiry Route.

Implements POST /api/v1/contact per P04 Contact specification.
Processes visitor inquiries, validates payload, and dispatches to neurachat.support@gmail.com.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, status

from backend.app.api.dependencies.services import ContactServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.contact import ContactRequestSchema, ContactResponseData
from backend.app.infrastructure.email.exceptions import (
    DuplicateSubmissionError,
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailDeliveryError,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

logger = get_logger("growflow.api.routes.contact")

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post(
    "",
    summary="Submit Public Contact Inquiry",
    description=(
        "Public endpoint accepting contact inquiries from visitors. "
        "Strictly validates inputs, prevents duplicate delivery, and securely dispatches "
        "an email to the authoritative GrowFlow mailbox (neurachat.support@gmail.com)."
    ),
    response_model=ContactResponseData,
    status_code=status.HTTP_201_CREATED,
)
async def submit_contact(
    payload: ContactRequestSchema,
    contact_service: ContactServiceDep,
) -> JSONResponse:
    """Process and dispatch visitor contact inquiry."""
    try:
        result = await contact_service.submit_inquiry(
            name=payload.name,
            email=payload.email,
            discussion_topic=payload.discussion_topic.value,
            message=payload.message,
        )

        response_data = ContactResponseData(
            submission_id=result.submission_id,
            status=result.status,
            timestamp=result.timestamp,
        ).model_dump()

        return success_response(
            message=result.message,
            data=response_data,
            status_code=status.HTTP_201_CREATED,
        )

    except DuplicateSubmissionError as exc:
        logger.warning("Duplicate contact submission rejected", error=exc.message)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc

    except EmailConfigurationError as exc:
        logger.error("Contact dispatch failed: email provider unconfigured", error=exc.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Contact delivery is temporarily unavailable. Please try again later or reach out via repository channels.",
        ) from exc

    except (EmailAuthenticationError, EmailDeliveryError) as exc:
        logger.error("Contact dispatch failed during email delivery", error=exc.message)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="We couldn't submit your message right now. Please try again in a moment.",
        ) from exc

    except Exception as exc:
        logger.error("Unexpected error processing contact inquiry", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request. Please try again.",
        ) from exc
