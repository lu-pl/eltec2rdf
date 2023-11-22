"""Functionality for parsing ELTeC XML file links and generating bindings."""

import abc
import collections

from dataclasses import dataclass, InitVar
from urllib.request import urlretrieve
from pathlib import Path

from lxml import etree

from eltec2rdf.extractors.xpath_extractors import (
    deu_extractors as deu,
    # spa_extractors as spa
)


@dataclass
class ELTeCPath:
    """Simple object representation for ELTeC raw links."""

    _eltec_url: InitVar

    def __post_init__(self, eltec_url):
        """Postinit hook for ELTeCPath."""
        _path = Path(eltec_url)

        self.url = eltec_url
        self.stem = _path.stem.lower()
        self.repo_id = _path.parts[3].lower()


class ELTeCBindingsGenerator(abc.ABC, collections.UserDict):
    """ABC for BindingGenerator."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize a BindingGenerator object."""
        self.eltec_url = eltec_url
        self.eltec_path = ELTeCPath(eltec_url)
        self.data = self.generate_bindings()

    def get_etree(self) -> etree._ElementTree:
        """Generate an ElementTree from an ELTec raw URL."""
        _temp_file_name, _ = urlretrieve(self.eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

        return tree

    @abc.abstractclassmethod
    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation.

        This method is responsible for /somehow/ generating dict data
        which is then used to init the UserDict of a BindingsGenerator.
        """
        raise NotImplementedError


class DEUBindingsGenerator(ELTeCBindingsGenerator):
    """ELTeC BindingsGenerator for the DEU corpus."""

    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation."""
        tree = self.get_etree()

        # bindings = {
        #     "url": self.eltec_path.url,
        #     "file_stem": self.eltec_path.stem,
        #     "repo_id": self.eltec_path.repo_id,
        #     "source_title": deu.get_source_title(tree),
        #     "source_ref": deu.get_source_ref(tree),
        #     "authors": deu.get_authors(tree),
        #     "sources": deu.get_sources(tree)
        # }

        bindings = {
            "url": self.eltec_path.url,
            "file_stem": self.eltec_path.stem,
            "repo_id": self.eltec_path.repo_id,
            "author": str,
            "author_ids": list,
            "work": str,
            'work_ids': list
        }

        return bindings


class SPABindingsGenerator(ELTeCBindingsGenerator):
    """ELTeC BindingsGenerator for the SPA corpus."""
