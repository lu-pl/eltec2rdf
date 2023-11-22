"""Functionality for parsing ELTeC XML file links and extracting bindings."""

import abc
import collections

from dataclasses import dataclass, InitVar
from urllib.request import urlretrieve
from pathlib import Path

from lxml import etree

from eltec2rdf.extractors.tree_extractors import (
    get_source_title,
    get_source_ref,
    get_sources,
    get_authors
)


@dataclass
class ELTeCPath:
    """Object representation for ELTeC raw links."""

    _eltec_url: InitVar

    def __post_init__(self, eltec_url):
        """Postinit hook for ELTeCPath."""
        _path = Path(eltec_url)

        self.url = eltec_url
        self.stem = _path.stem.lower()
        self.repo_id = _path.parts[3].lower()


class ELTeCBindingsExtractor(abc.ABC, collections.UserDict):
    """ABC for BindingExtractors."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize a BindingExtractor object."""
        self.eltec_url = eltec_url
        self.eltec_path = ELTeCPath(eltec_url)
        self.data = self.generate_bindings()

    @abc.abstractclassmethod
    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation.

        This method is responsible for /somehow/ generating dict data
        which is then used to init the UserDict of a BindingsExtractor.
        """
        raise NotImplementedError


class DEUBindingsExtractor(ELTeCBindingsExtractor):
    """ELTeC BindingsExtractor for the DEU corpus."""

    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self.eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

        bindings = {
            "source_title": get_source_title(tree),
            "source_ref": get_source_ref(tree),
            "url": self.eltec_path.url,
            "file_stem": self.eltec_path.stem,
            "repo_id": self.eltec_path.repo_id,
            "authors": get_authors(tree),
            "sources": get_sources(tree)
        }

        return bindings


class SPABindingsExtractor(ELTeCBindingsExtractor):
    """ELTeC BindingsExtractor for the SPA corpus."""
