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
    # get author name from titleStmt instead
    # author_name=digital_source("tei:author/text()"),
    author_name="//tei:titleStmt/tei:author/text()",
    author_id="//tei:titleStmt/tei:author/@ref",
    source_title=digital_source("tei:title/text()"),
    source_ref=digital_source("tei:ref/@target"),
)

TEIXPath: Callable[[etree.ElementTree], Any] = partial(
    etree.XPath,
    namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
)

xpath_definitions = {
    "author_name": TEIXPath(xpaths.author_name),
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
        return re.sub(r"\s{2,}", " ", "".join(bibl)).strip()

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

    @staticmethod
    def _get_id_type_dict(ref_id: str) -> Mapping[str, str]:
        """..."""
        _parts = list(filter(bool, re.split(r"[/:]", ref_id)))
        _pairs = zip(
            ("id_type", "id_value", "id_full"),
            (*_parts[-2:], ref_id)
        )

        return dict(_pairs)

    def _get_author_ids(self, xpath_result: str) -> list[Mapping]:
        """..."""
        if not xpath_result:
            return None

        _ids = filter(
            lambda x: x.find("missing") == -1,
            xpath_result.split(" ")
        )

        author_ids = [
            self._get_id_type_dict(_id)
            for _id in _ids
        ]

        return author_ids

    def _get_bindings(self) -> Mapping:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self.eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

            _xpath_bindings = toolz.valmap(
                lambda x: self._get_bibl(x(tree)[0]) if x(tree) else None,
                xpath_definitions
            )

        _eltec_path = Path(self.eltec_url)

        try:
            _author_id: str = TEIXPath(xpaths.author_id)(tree)[0]
        except IndexError:
            _author_id = ""

        _base_bindings = {
            "url": self.eltec_url,
            "file_stem": _eltec_path.stem.lower(),
            "repo_id": _eltec_path.parts[3].lower(),
            "author_id": self._get_author_ids(_author_id),
            "other_sources": list(self._get_other_sources(tree))
        }

        bindings = {**_xpath_bindings, **_base_bindings}
        return bindings
