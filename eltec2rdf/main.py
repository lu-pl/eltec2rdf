"""Public entry point for the eltec2rdf script."""

from collections.abc import Iterator
from pathlib import Path

from clisn import CLSInfraNamespaceManager
from lodkit.graph import Graph
from loguru import logger


from eltec2rdf.extractors.bindings_extractor import ELTeCBindingsExtractor
from eltec2rdf.extractors.link_extractor import get_eltec_xml_links
from eltec2rdf.rdfgenerators import CLSCorGenerator


REPOS: list[str] = [
    "ELTeC-eng",
    "ELTeC-deu",
    "ELTeC-cze",
    "ELTeC-fra",
    "ELTeC-spa",
]


def generate_graph(repo: str) -> Graph:
    """Process an ELTeC repo, generate a graph and serialize to output file."""
    uris: Iterator[str] = get_eltec_xml_links(repos=[repo])

    _output_file_name: str = f'{repo.lower().replace("-", "_")}.ttl'
    output_file = Path(f"./output/{_output_file_name}")

    g = Graph()
    CLSInfraNamespaceManager(g)

    for uri in uris:
        bindings = ELTeCBindingsExtractor(uri)
        triples = CLSCorGenerator(**bindings)

        logger.info(f"Generating triples for {Path(uri).stem}")

        for triple in triples:
            g.add(triple)

    with open(output_file, "w") as f:
        f.write(g.serialize())


if __name__ == "__main__":
    for repo in REPOS:
        generate_graph(repo)
