"""Validate model responses before treating them as review evidence."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


NonEmptyText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
Confidence = Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]


class ContentIssueOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    snippet: NonEmptyText
    reason: NonEmptyText
    confidence: Confidence
    rule_code: NonEmptyText | None = None


class ContentCheckOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Missing/null issues is not equivalent to a successful empty result.
    issues: list[ContentIssueOutput]


class ChatMessageOutput(BaseModel):
    content: NonEmptyText


class ChatChoiceOutput(BaseModel):
    message: ChatMessageOutput


class ChatCompletionOutput(BaseModel):
    choices: Annotated[list[ChatChoiceOutput], Field(min_length=1)]


def validate_task_output(code: str, value: dict) -> dict:
    if code == "CONTENT_CHECK":
        return ContentCheckOutput.model_validate(value).model_dump()
    # Other existing callers include the connection test, not a content review.
    return value
