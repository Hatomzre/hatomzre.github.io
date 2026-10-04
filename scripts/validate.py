#!/usr/bin/env python3
"""Validate the rendered static site and its public-content boundary."""

from __future__ import annotations

import re
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASE_URL = json.loads((ROOT / "profile.yml").read_text(encoding="utf-8"))["website"]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[str] = []
        self.main_count = 0
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        self.main_count += tag == "main"
        self.h1_count += tag == "h1"
        for attribute in ("href", "src"):
            if attributes.get(attribute):
                self.references.append(attributes[attribute])


required = [
    "index.html",
    "research/index.html",
    "publications/index.html",
    "teaching/index.html",
    "cv/index.html",
    "robots.txt",
    "sitemap.xml",
    "assets/images/og-default.png",
    "assets/images/favicon.png",
    "assets/images/portrait.webp",
    "assets/images/life/hkust-clear-water-bay.webp",
    "assets/images/life/travel-portrait.webp",
]

for relative in required:
    if not (SITE / relative).is_file():
        fail(f"Missing rendered file: {relative}")

if list(SITE.rglob("*.pdf")) or list((ROOT / "assets").rglob("*.pdf")):
    fail("The owner has not approved publication of a PDF CV. Remove PDF files from public assets and output.")

html_pages = [
    SITE / "index.html",
    SITE / "research/index.html",
    SITE / "publications/index.html",
    SITE / "teaching/index.html",
    SITE / "cv/index.html",
]
parsed_pages: dict[Path, PageLinks] = {}
for page in html_pages:
    content = page.read_text(encoding="utf-8")
    parsed = PageLinks()
    parsed.feed(content)
    parsed_pages[page.resolve()] = parsed
    if parsed.main_count != 1 or parsed.h1_count < 1:
        fail(f"{page.relative_to(SITE)} must have one main landmark and a primary heading.")
    for marker in ('rel="canonical"', 'property="og:title"', 'application/ld+json'):
        if marker not in content:
            fail(f"{page.relative_to(SITE)} lacks {marker}")
    if "yt.huang@connect.ust.hk" not in content:
        fail(f"{page.relative_to(SITE)} lacks the approved contact email")

internal_references = 0
for page, parsed in parsed_pages.items():
    for reference in parsed.references:
        url = urlsplit(reference)
        if not url.scheme and url.path.lower().endswith(".pdf"):
            fail(f"Unapproved local PDF link in {page.relative_to(SITE)}: {reference}")
        if url.scheme or url.netloc:
            continue
        target = (SITE / unquote(url.path).lstrip("/") if url.path.startswith("/")
                  else page.parent / unquote(url.path)) if url.path else page
        target = target.resolve()
        if not target.is_relative_to(SITE.resolve()):
            fail(f"Local reference escapes the site: {reference}")
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            fail(f"Broken local reference in {page.relative_to(SITE)}: {reference}")
        if url.fragment and target in parsed_pages:
            if unquote(url.fragment) not in parsed_pages[target].ids:
                fail(f"Broken anchor in {page.relative_to(SITE)}: {reference}")
        internal_references += 1

robots = (SITE / "robots.txt").read_text(encoding="utf-8")
if f"Sitemap: {BASE_URL}sitemap.xml" not in robots:
    fail("robots.txt does not point at the production sitemap.")

sitemap = ET.parse(SITE / "sitemap.xml")
locations = [node.text for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
expected_locations = [BASE_URL + route for route in ("", "research/", "publications/", "teaching/", "cv/")]
if locations != expected_locations:
    fail("Sitemap addresses must exactly match the five canonical routes.")

prohibited = [
    r"grain\s+boundary\s+grooving",
    r"KWC[- ]Based",
    r"graph\s+neural\s+networks?.{0,80}\b(?:architecture|layers?|training|dataset|accuracy|benchmark|performance|results?)\b",
    r"\bGNN\b.{0,80}\b(?:architecture|layers?|training|dataset|accuracy|benchmark|performance|results?)\b",
    r"pending\s+publication",
    r"\bin\s+preparation\b",
    r"unpublished\s+(?:figure|result|dataset)",
    r"64676876",
]
source_suffixes = {".qmd", ".yml", ".yaml", ".md", ".html", ".bib"}
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in source_suffixes:
        continue
    if any(part in {"scripts", ".git"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in prohibited:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"Confidentiality check matched {pattern!r} in {path.relative_to(ROOT)}")

print(f"Validation passed: {len(html_pages)} pages, {internal_references} local references, "
      "landmarks, metadata, imagery, sitemap, PDF exclusion, and confidentiality boundary are intact.")
