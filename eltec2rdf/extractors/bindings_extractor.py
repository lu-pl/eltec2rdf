"""Functionality for parsing ELTeC XML file links and extracting bindings."""

import collections
import re

from collections.abc import Callable, Mapping, Iterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from urllib.request import urlretrieve
from pathlib import Path

import toolz

from lxml import etree


@dataclass
class XPaths:
    """Dataclass for XPath path definitions."""

    author_name: str
    author_id: str
    source_title: str
    source_ref: str


def digital_source(partial_xpath: str):
    """Expand an XPath shortcut for 'digitalSource'."""
    _digi_source = "//tei:sourceDesc/tei:bibl[@type='digitalSource']/"
    _partial = partial_xpath.lstrip("/")
    return f"{_digi_source}{_partial}"


xpaths = XPaths(
    author_name=digital_source("tei:author/text()"),
    author_id="//tei:titleStmt/tei:author/@ref",
    source_title=digital_source("tei:title/text()"),
    source_ref=digital_source("tei:ref/@target"),
)

TEIXPath: Callable[[etree.ElementTree], Any] = partial(
    etree.XPath,
    namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
)

xpath_definitions = {
    "source_author": TEIXPath(xpaths.author_name),
    "author_gnd_url": TEIXPath(xpaths.author_id),
    "source_title": TEIXPath(xpaths.source_title),
    "source_ref": TEIXPath(xpaths.source_ref)
}


class ELTeCBindingsExtractor(collections.UserDict):
    """Binding Representation for an ELTeC resource."""

    def __init__(self, eltec_url):
        """Initialize an ELTeCBindingsExtractor instance."""
        self.eltec_url = eltec_url
        self.data = self._get_bindings()

    @staticmethod
    def _get_bibl(bibl: str) -> str:
        """Sanitize bibliographic reference strings.

        Used for tei:sourceDesc bibls.
        """
        return re.sub(r"\s{2,}", " ", "".join(bibl))

    def _get_other_sources(
            self,
            tree: etree._ElementTree
    ) -> Iterator[Mapping]:
        """Extract bibls from tei:sourceDesc (excluding 'digitalSource').

        Used in self._get_bindings along the 'other_sources' key.
        """
        _elements_path = TEIXPath(
            "//tei:sourceDesc/tei:bibl[not(@type='digitalSource')]"
        )
        elements: list[etree._Element] = _elements_path(tree)

        return map(
            lambda element: {
                "type": element.get("type"),
                "title": self._get_bibl(element.xpath(".//text()"))
            },
            elements
        )

    def _get_bindings(self) -> Mapping:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self.eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

            _xpath_bindings = toolz.valmap(
                lambda x: x(tree)[0],
                xpath_definitions
            )

        _eltec_path = Path(self.eltec_url)
        _base_bindings = {
            "url": self.eltec_url,
            "file_stem": _eltec_path.stem.lower(),
            "repo_id": _eltec_path.parts[3].lower(),
            "author_gnd_id": Path(_xpath_bindings["author_gnd_url"]).stem,
            "other_sources": list(self._get_other_sources(tree))
        }

        bindings = {**_xpath_bindings, **_base_bindings}
        return bindings
