"""Functionality for parsing ELTeC XML file links and extracting bindings."""

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


class ELTeCBindingsExtractor(collections.UserDict):
    """Binding Representation for an ELTeC resource."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize a BindingExtractor object."""
        self._eltec_url = eltec_url
        self._eltec_path = ELTeCPath(eltec_url)
        self.data = self._generate_bindings()

    def _generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self._eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

        bindings = {
            "source_title": get_source_title(tree),
            "source_ref": get_source_ref(tree),
            "url": self._eltec_path.url,
            "file_stem": self._eltec_path.stem,
            "repo_id": self._eltec_path.repo_id,
            "authors": get_authors(tree),
            "sources": get_sources(tree)
        }

        return bindings
