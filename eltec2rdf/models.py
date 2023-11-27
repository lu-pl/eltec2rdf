"""Pydantic models for RDFGenerator bindings validation."""

from pydantic import BaseModel, ConfigDict


class BindingsBaseModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: list | None = None
    work_ids: list | None = None
