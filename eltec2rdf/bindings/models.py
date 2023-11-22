"""Pydantic models for bindings validation."""

from pydantic import BaseModel


class _BindingsModel(BaseModel):
    """Pydantic BaseModel for ELTeC bindings."""

    url: str
    file_stem: str
    repo_id: str


class DEUBindingsModel(_BindingsModel):
    """Pydantic Model for ELTeC DEU bindings."""


class SPABindingsModel(_BindingsModel):
    """Pydantic Model for ELTeC SPA bindings."""
