"""Kebab-case names for skills and demos."""

import re


def kebab(name: str) -> str:
    """Lower-case ``name`` and join its words with hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
