#!/usr/bin/env python3
"""Keep the sitemap aligned with the canonical addresses of the five public pages."""

import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
ROUTES = ("", "research/", "publications/", "teaching/", "cv/")
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class CanonicalParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel") == "canonical":
            self.urls.append(attributes.get("href"))


def main():
    base = json.loads((ROOT / "profile.yml").read_text(encoding="utf-8"))["website"]
    ET.register_namespace("", NS)
    sitemap = ET.Element(f"{{{NS}}}urlset")
    for route in ROUTES:
        parser = CanonicalParser()
        parser.feed((SITE / route / "index.html").read_text(encoding="utf-8"))
        expected = base + route
        if parser.urls != [expected]:
            raise ValueError(f"Canonical address mismatch for {route or '/'}: {parser.urls}; expected {expected}")
        url = ET.SubElement(sitemap, f"{{{NS}}}url")
        ET.SubElement(url, f"{{{NS}}}loc").text = expected
    ET.indent(sitemap, space="  ")
    ET.ElementTree(sitemap).write(SITE / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print("Sitemap finalized: five canonical page addresses.")


if __name__ == "__main__":
    main()
