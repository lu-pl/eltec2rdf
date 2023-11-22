"""Pydantic models for bindings validation."""

from pydantic import BaseModel, Field


class Bindings(BaseModel):
    """Pydantic BaseModel for ELTeC bindings."""

    raw_link: str
    file_stem: str
    repo_id: str

    work_title: str
    author_name: str
    work_ids: list = Field(default_factory=list)
    author_ids: list = Field(default_factory=list)
