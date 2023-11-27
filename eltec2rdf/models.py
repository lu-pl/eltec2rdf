"""Pydantic models for RDFGenerator bindings validation."""

from pydantic import BaseModel, ConfigDict


class BindingsBaseModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    # specify fields
