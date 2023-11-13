"""Functionality for extracting XML file links from the ELTeC repo."""

import re
import os

from collections.abc import Iterator

from github import Github, Auth
from dotenv import load_dotenv


# get token
load_dotenv()
token = os.getenv("TOKEN")
auth = Auth.Token(token)

g = Github(auth=auth)


def _get_raw_links(repository: str) -> Iterator[str]:
    """Get raw XML file links from level1 of an ELTeC repo."""
    repo = g.get_repo(repository)
    contents = repo.get_contents("")

    try:
        level1_dir = next(filter(lambda x: x.name == "level1", contents))
    except StopIteration:
        print(f"INFO: No 'level1' for '{repository}'.")
        return None

    for f in repo.get_contents(level1_dir.path):
        download_url = f.download_url
        if download_url and download_url.endswith(".xml"):
            yield download_url


def _get_user_repos(username: str):
    """Get all repos given a Github username."""
    user = g.get_user(username)
    user_repos = user.get_repos()

    for repo in user_repos:
        yield repo


def _get_eltec_corpus_repos() -> Iterator[str]:
    """Filter down ELTeC repos for corpora repos.."""
    eltec_repos = _get_user_repos("COST-ELTeC ")

    for repo in eltec_repos:
        repo_name = repo.name
        if re.match(r"ELTeC-.+", repo_name):
            yield repo_name


def get_eltec_level1_xml():
    """Get XML file links from level1 folders across all ELTec repos."""
    corpus_repo_names = _get_eltec_corpus_repos()

    for repo_name in corpus_repo_names:
        full_repo_name = f"COST-ELTeC/{repo_name}"
        yield from _get_raw_links(full_repo_name)
