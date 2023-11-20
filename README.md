# eltec2rdf
Script for generating RDF based on ELTeC XML resources.

## Requirements

* Python >= 3.11

The script also expects a valid Github API token named "TOKEN" to be present in `.env`.

E.g. in `eltec2rdf/.env`: 
```text
TOKEN=<valid_github_api_token>
```

## Installation

Either use [poetry](https://python-poetry.org/) or activate a virtual environment (Python >=3.11) and run the following commands:
```shell
git clone git@github.com:lu-pl/eltec2rdf.git
cd eltec2rdf/
pip install .
```
