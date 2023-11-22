"""Extractors for pulling data from TEI/XML for use in bindings_extractor.

THIS IS A MERE COPY OF THE OLD tree_extractors!!!
"""

import re

from collections.abc import Iterator, Mapping
from functools import partial, wraps

from loguru import logger
from lxml import etree


TEIXPath = partial(
    etree.XPath,
    namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
)


def _repr(string: str):
    """Sanitize strings by eliminating superfluous whitespace."""
    return re.sub(r"\s{2,}", " ", "".join(string)).strip()


def _repr_title_stmt(value: str) -> str:
    """Sanitize strings extracted from tei:titleStmts."""
    re_result = re.sub(
        string=value,
        pattern=r"[:\(].*eltec.*",
        repl="",
        flags=re.I
    )

    return _repr(re_result)


def _digital_source(partial_xpath: str):
    """Expand an XPath shortcut for 'digitalSource'."""
    _digi_source = "//tei:sourceDesc/tei:bibl[@type='digitalSource']/"
    _partial = partial_xpath.lstrip("/")
    return f"{_digi_source}{_partial}"


def _from_sourcedesc(tree: etree._ElementTree) -> str | None:
    xpath_result = TEIXPath(_digital_source("tei:title/text()"))(tree)

    if xpath_result:
        return _repr(xpath_result[0])

    return None


def _from_titlestmt(tree: etree._ElementTree) -> str | None:
    xpath_result = TEIXPath("//tei:titleStmt/tei:title/text()")(tree)

    if xpath_result:
        _title = xpath_result[0]
        return _repr_title_stmt(_title)

    return None


def get_source_title(tree: etree._ElementTree) -> str | None:
    """Extract a source title from a TEI ElementTree."""
    result = (
        _from_sourcedesc(tree)
        or
        _from_titlestmt(tree)
        or
        None
    )

    return result


def get_source_ref(tree: etree._ElementTree):
    """..."""
    xpath_result = TEIXPath(_digital_source("tei:ref/@target"))(tree)

    if xpath_result:
        return xpath_result[0]

    return None


def get_sources(tree: etree._ElementTree) -> list[dict]:
    """Extract bibls from tei:sourceDesc."""
    elements = TEIXPath("//tei:sourceDesc/tei:bibl")(tree)

    result = map(
        lambda element: {
            "type": element.get("type"),
            "title": _repr(TEIXPath("tei:title/text()")(element)),
            "ref": TEIXPath("tei:ref/@target")(element)
        },
        elements
    )

    return list(result)


def get_authors(tree: etree._ElementTree) -> list:
    """..."""
    elements = TEIXPath("//tei:titleStmt/tei:author")(tree)

    result = map(
        lambda element: {
            "name": _repr(element.xpath(".//text()")),
            "ref": element.get("ref")
        },
        elements
    )

    return list(result)
