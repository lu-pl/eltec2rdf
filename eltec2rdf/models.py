"""Pydantic models for RDFGenerator bindings validation."""

from collections.abc import Mapping
from pydantic import BaseModel, ConfigDict


class BindingsBaseModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: Mapping | None = None
    work_ids: Mapping | None = None
