"""..."""

from collections.abc import Mapping

from eltec2rdf.extractors import ELTeCBindingsExtractor

from lodkit.graph import Graph


class ELTeCConverter:
    """Converter for RDF generation based on an ELTec resource."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize an ELTeCConverter instance."""
        self._eltec_url = eltec_url
        self._graph = Graph()

        self.bindings = ELTeCBindingsExtractor(self._eltec_url)

    def _generate_graph(self, bindings: Mapping) -> Graph:
        """Generate a graph instance from an ELTeC resource.

        Bindings are optained by querying the ELTec source
        with self._get_bindings.
        """
        ...
        return self._graph


# adhoc testing
eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-deu/master/level1/DEU007.xml"
converter = ELTeCConverter(eltec_url)
print("bindings: ", converter.bindings)
