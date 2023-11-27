"""Pydantic models for RDFGenerator bindings validation."""

from collections.abc import Iterator
from typing import Literal

from rdflib.namespace import RDFS
from pydantic import BaseModel, ConfigDict

from eltec2rdf.vocabs.vocabs import vocab_graph


# better list cast here, else the iterator will likely be exhausted somewhere
vocab_types: list[str] = list(map(str, vocab_graph.objects(None, RDFS.label)))


class IDMapping(BaseModel):
    """Simple model for IDMappings."""

    id_type: Literal[*vocab_types] | None = None
    id_value: str | None = None


class BindingsBaseModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: IDMapping | None = None
    work_ids: IDMapping | None = None
