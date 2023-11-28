"""Extractors for pulling data from TEI/XML for use in bindings_extractor."""

import re

from functools import partial
from typing import Literal

from lxml import etree
from eltec2rdf.models import vocab_types


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


def _get_title_from_sourcedesc(tree: etree._ElementTree) -> str | None:
    """Try to get source_title from sourceDesc.

    XPath extractor for get_source_title.
    """
    xpath_result = TEIXPath(_digital_source("tei:title/text()"))(tree)

    if xpath_result:
        return _repr(xpath_result[0])

    return None


def _get_title_from_titlestmt(tree: etree._ElementTree) -> str | None:
    """Try to get source_title from titleStmt.

    XPath extractor for get_source_title.
    """
    xpath_result = TEIXPath("//tei:titleStmt/tei:title/text()")(tree)

    if xpath_result:
        _title = xpath_result[0]
        return _repr_title_stmt(_title)

    return None


def _get_id_type(id_value: str, _fail_value=None) -> Literal[*vocab_types] | None:
    """Primitive callabe for determining the id_type of an id_value.

    This merely performs a string containment check lol.
    """
    for id_type in vocab_types:
        if id_type in id_value:
            return id_type

    return _fail_value


def get_work_title(tree: etree._ElementTree) -> str | None:
    """Extract a source title from a TEI ElementTree."""
    result = (
        _get_title_from_sourcedesc(tree)
        or
        _get_title_from_titlestmt(tree)
        or
        None
    )

    return result


def get_author_name(tree: etree._ElementTree) -> str:
    """Extract the author name from tei:titleStmt."""
    _name = TEIXPath("//tei:titleStmt/tei:author/text()")(tree)
    return _repr(_name)


def get_work_ids(tree: etree._ElementTree) -> list[dict]:
    """Try to extract workd ids from a tree.

    The returned dict is expected to validate against IDMapping.
    If no ids can be retrieved, return an empty dict,
    else the validator will fail.
    """
    # deu/spa: sourceDesc/bibl/ref/@target; maybe record the bibl type?
    _work_ids = TEIXPath("//tei:sourceDesc/tei:bibl/tei:ref/@target")(tree)
    return [
        {
            "id_type": _get_id_type(work_id),
            "id_value": work_id
        }
        for work_id in _work_ids
    ]


def get_author_ids(tree: etree._ElementTree) -> list[dict]:
    """Try to extract author ids from a tree.

    The returned dict is expected to validate against IDMapping.
    If no ids can be retrieved, return an empty dict,
    else the validator will fail.
    """
    # deu/spa: titleStmt/author/@ref
    _author_ids = TEIXPath("//tei:titleStmt/tei:author/@ref")(tree)
    return [
        {
            "id_type": _get_id_type(author_id),
            "id_value": author_id
        }
        for author_id in _author_ids
    ]
