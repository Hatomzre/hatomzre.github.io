#!/usr/bin/env python3
"""Render site fragments from the project's JSON-compatible YAML sources."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "_generated"
INCLUDES = ROOT / "includes"


def load_data(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write(relative: str, content: str) -> None:
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def raw_html(content: str) -> str:
    """Keep generated nested markup out of Pandoc's indented-code parser."""
    return "```{=html}\n" + content.rstrip() + "\n```"


def parse_bibtex(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        start = match.end()
        depth = 1
        cursor = start
        while cursor < len(text) and depth:
            if text[cursor] == "{":
                depth += 1
            elif text[cursor] == "}":
                depth -= 1
            cursor += 1
        block = text[start : cursor - 1]
        entry: dict[str, str] = {"type": match.group(1), "key": match.group(2).strip()}
        for line in block.splitlines():
            field = re.match(r"\s*([A-Za-z]+)\s*=\s*\{(.*)\}\s*,?\s*$", line)
            if field:
                entry[field.group(1).lower()] = field.group(2).strip()
        entries.append(entry)
    return entries


def render_links(profile: dict) -> str:
    links = [
        ("Email", f"mailto:{profile['email']}"),
        ("GitHub", profile["github"]),
    ]
    if profile.get("scholar"):
        links.append(("Google Scholar", profile["scholar"]))
    if profile.get("orcid"):
        links.append(("ORCID", profile["orcid"]))
    anchors = "\n".join(
        f'<a class="profile-link" href="{esc(url)}">{esc(label)}</a>' for label, url in links
    )
    return f'<div class="profile-links" aria-label="Researcher links">\n{anchors}\n</div>'


def render_teaching(teaching: list[dict]) -> str:
    cards = []
    for item in teaching:
        cards.append(
            "\n".join(
                [
                    '<article class="teaching-card">',
                    f'  <p class="course-code">{esc(item["code"])}</p>',
                    f'  <h3>{esc(item["title"])}</h3>',
                    f'  <p class="course-meta">{esc(item["role"])} · <span class="course-term">{esc(item["term"])}</span></p>',
                    "</article>",
                ]
            )
        )
    return '<div class="teaching-grid">\n' + "\n".join(cards) + "\n</div>"


def render_talks(talks: list[dict]) -> str:
    items = []
    for talk in talks:
        items.append(
            "\n".join(
                [
                    '<li class="timeline-item">',
                    f'  <span class="timeline-year">{esc(talk["year"])}</span>',
                    '  <div class="timeline-copy">',
                    f'    <h3>{esc(talk["title"])}</h3>',
                    f'    <p>{esc(talk["event"])} · {esc(talk["location"])}</p>',
                    "  </div>",
                    "</li>",
                ]
            )
        )
    return '<ol class="timeline">\n' + "\n".join(items) + "\n</ol>"


def render_interests(interests: list[str]) -> str:
    cards = []
    labels = ["Phase-field modeling", "Physics-based neural modeling", "Graph neural networks"]
    for label, interest in zip(labels, interests):
        cards.append(
            f'<article class="interest-card"><h3>{esc(label)}</h3><p>{esc(interest)}</p></article>'
        )
    return '<div class="interest-grid">\n' + "\n".join(cards) + "\n</div>"


def schematic(project_id: str) -> str:
    if project_id == "amorphization":
        return """
<div class="schematic schematic-amorphization" role="img" aria-label="Abstract schematic of crystalline grains crossed by an amorphous shear band">
  <div class="grain grain-a" aria-hidden="true"></div>
  <div class="grain grain-b" aria-hidden="true"></div>
  <div class="grain grain-c" aria-hidden="true"></div>
  <div class="grain grain-d" aria-hidden="true"></div>
  <div class="shear-band" aria-hidden="true"></div>
  <span class="schematic-label label-crystal">crystalline</span>
  <span class="schematic-label label-band">amorphous band</span>
</div>""".strip()
    return """
<div class="schematic schematic-dislocations" role="img" aria-label="Abstract energy landscape showing dislocations relaxing toward a stable configuration">
  <div class="energy-line energy-one" aria-hidden="true"></div>
  <div class="energy-line energy-two" aria-hidden="true"></div>
  <span class="dislocation d-one" aria-hidden="true">⊥</span>
  <span class="dislocation d-two" aria-hidden="true">⊤</span>
  <span class="dislocation d-three" aria-hidden="true">⊥</span>
  <span class="schematic-label label-energy">interaction energy</span>
  <span class="schematic-label label-stable">stable state</span>
</div>""".strip()


def render_research(projects: list[dict]) -> str:
    sections = []
    for index, project in enumerate(projects):
        links = " ".join(
            f'<a class="text-link" href="{esc(link["url"])}">{esc(link["label"])}</a>'
            for link in project["links"]
        )
        copy = "\n".join(
            [
                '<div class="case-study-header">',
                f'  <p class="eyebrow">{esc(project["label"])}</p>',
                f'  <h2>{esc(project["title"])}</h2>',
                '</div>',
                '<div class="case-study-body">',
                '  <h3 class="case-kicker">The question</h3>',
                f'  <p>{esc(project["question"])}</p>',
                '  <h3 class="case-kicker">The approach</h3>',
                f'  <p>{esc(project["approach"])}</p>',
                '  <h3 class="case-kicker">The contribution</h3>',
                f'  <p>{esc(project["contribution"])}</p>',
                f'  <div class="case-links">{links}</div>',
                "</div>",
            ]
        )
        sections.append(
            f'<section id="{esc(project["id"])}" class="case-study">\n' + copy + "\n</section>"
        )
    return "\n".join(sections)


def render_selected_publications(entries: list[dict[str, str]]) -> str:
    selected = [entry for entry in entries if entry.get("selected", "false").lower() == "true"]
    return render_publications(selected, heading_level=3)


def format_authors(author_field: str) -> str:
    formatted = []
    for author in author_field.split(" and "):
        author = author.strip()
        if "," in author:
            family, given = [part.strip() for part in author.split(",", 1)]
            display = f"{given} {family}"
        else:
            display = author
        if display.casefold() == "yuntong huang":
            display = f"<strong>{esc(display)}</strong>"
        else:
            display = esc(display)
        formatted.append(display)
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return " and ".join(formatted)
    return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def render_publications(entries: list[dict[str, str]], heading_level: int = 2) -> str:
    cards = []
    for entry in sorted(entries, key=lambda item: item.get("year", ""), reverse=True):
        venue = entry.get("journal", entry.get("note", "Public preprint"))
        details = []
        if entry.get("volume"):
            details.append(entry["volume"])
        if entry.get("pages"):
            details.append(entry["pages"].replace("--", "-") )
        citation_tail = ", ".join(details)
        if citation_tail:
            venue = f"{venue} {citation_tail}"
        links = []
        if entry.get("doi"):
            links.append(("DOI", f'https://doi.org/{entry["doi"]}'))
        elif entry.get("url"):
            links.append(("arXiv", entry["url"]))
        if entry.get("preprint"):
            links.append(("Preprint", entry["preprint"]))
        anchors = " ".join(
            f'<a class="text-link" href="{esc(url)}">{esc(label)}</a>' for label, url in links
        )
        publication_type = "Journal article" if entry.get("type") == "article" else "Preprint"
        cards.append(
            "\n".join(
                [
                    '<article class="publication-full">',
                    f'  <span class="publication-year">{esc(entry.get("year", ""))}</span>',
                    f'  <h{heading_level}><a href="{esc(entry.get("url", "#"))}">{esc(entry.get("title", ""))}</a></h{heading_level}>',
                    f'  <p class="publication-authors">{format_authors(entry.get("author", ""))}</p>',
                    f'  <p class="publication-venue"><em>{esc(venue)}</em> ({esc(entry.get("year", ""))}).</p>',
                    f'  <div class="publication-links">{anchors}<span class="publication-type">{publication_type}</span></div>',
                    "</article>",
                ]
            )
        )
    return '<div class="publication-list">\n' + "\n".join(cards) + "\n</div>"


def render_awards(profile: dict) -> str:
    items = []
    for award in profile["awards"]:
        items.append(
            f'<article><span>{esc(award["year"])}</span><h3>{esc(award["name"])}</h3><p>{esc(award["organization"])}</p></article>'
        )
    return '<div class="award-grid">\n' + "\n".join(items) + "\n</div>"


def render_service(profile: dict) -> str:
    items = []
    for item in profile["service"]:
        items.append(f'- **{item["role"]}**, {item["event"]} · {item["year"]}')
    return "\n".join(items)


def render_head(profile: dict) -> str:
    same_as = [profile["github"]]
    same_as.extend(url for url in [profile.get("scholar"), profile.get("orcid")] if url)
    person = {
        "@type": "Person",
        "@id": f'{profile["website"]}#person',
        "name": profile["name"],
        "alternateName": profile["alternate_name"],
        "givenName": profile["given_name"],
        "familyName": profile["family_name"],
        "url": profile["website"],
        "image": profile["website"] + profile["portrait"],
        "jobTitle": profile["role"],
        "email": f'mailto:{profile["email"]}',
        "affiliation": {
            "@type": "CollegeOrUniversity",
            "name": profile["affiliation"],
            "sameAs": "https://hkust.edu.hk/",
        },
        "knowsAbout": profile["knows_about"],
        "sameAs": same_as,
    }
    website = {
        "@type": "WebSite",
        "@id": f'{profile["website"]}#website',
        "url": profile["website"],
        "name": profile["name"],
        "inLanguage": "en",
        "about": {"@id": person["@id"]},
        "publisher": {"@id": person["@id"]},
    }
    profile_page = {
        "@type": "ProfilePage",
        "@id": f'{profile["website"]}#profilepage',
        "url": profile["website"],
        "name": f'{profile["name"]} — Academic Profile',
        "inLanguage": "en",
        "mainEntity": {"@id": person["@id"]},
        "isPartOf": {"@id": website["@id"]},
    }
    graph = {
        "@context": "https://schema.org",
        "@graph": [person, profile_page, website],
    }
    parts = [
        '<meta name="theme-color" content="#FFFFFF">',
        '<meta name="color-scheme" content="light dark">',
        '<script type="application/ld+json">',
        json.dumps(graph, ensure_ascii=False, indent=2),
        "</script>",
    ]
    verification = profile.get("analytics", {}).get("google_site_verification")
    if verification:
        parts.append(f'<meta name="google-site-verification" content="{esc(verification)}">')
    token = profile.get("analytics", {}).get("cloudflare_token")
    if token:
        beacon = json.dumps({"token": token}, separators=(",", ":"))
        parts.append(
            '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
            f"data-cf-beacon='{esc(beacon)}'></script>"
        )
    return "\n".join(parts)


def render_footer(profile: dict) -> str:
    links = [
        ("HKUST", "https://hkust.edu.hk/"),
        ("Email", f'mailto:{profile["email"]}'),
        ("GitHub", profile["github"]),
    ]
    if profile.get("scholar"):
        links.append(("Google Scholar", profile["scholar"]))
    if profile.get("orcid"):
        links.append(("ORCID", profile["orcid"]))
    links.append(("CV", "/cv/"))
    anchors = "\n    ".join(
        f'<a href="{esc(url)}">{esc(label)}</a>' for label, url in links
    )
    return "\n".join(
        [
            '<footer class="site-footer">',
            f'  <p>© 2026 {esc(profile["name"])} · Mathematics, {esc(profile["affiliation_short"])}</p>',
            '  <nav aria-label="Footer navigation">',
            f"    {anchors}",
            "  </nav>",
            "</footer>",
        ]
    )


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    INCLUDES.mkdir(parents=True, exist_ok=True)
    profile = load_data("profile.yml")
    teaching = load_data("data/teaching.yml")
    talks = load_data("data/talks.yml")
    research = load_data("data/research.yml")
    publications = parse_bibtex(ROOT / "publications.bib")

    write("_generated/profile-links.md", raw_html(render_links(profile)))
    write("_generated/availability.md", raw_html(
        f'<p class="postdoc-note">Expected PhD graduation: {esc(profile["expected_completion"])}.<br>'
        f'<strong>{esc(profile["availability"])}</strong></p>'
    ))
    write("_generated/teaching.md", raw_html(render_teaching(teaching)))
    write("_generated/teaching-summary.md", raw_html(
        '<p>' + ' · '.join(esc(item["code"]) for item in teaching) + '</p>'
    ))
    write("_generated/talks.md", raw_html(render_talks(talks)))
    write("_generated/interests.md", raw_html(render_interests(research["interests"])))
    write(
        "_generated/research-projects.md",
        raw_html(render_research(research["public_projects"])),
    )
    write(
        "_generated/selected-publications.md",
        raw_html(render_selected_publications(publications)),
    )
    write("_generated/publications.md", raw_html(render_publications(publications)))
    write("_generated/awards.md", raw_html(render_awards(profile)))
    write("_generated/service.md", render_service(profile))
    write("includes/head.html", render_head(profile))
    write("includes/footer.html", render_footer(profile))
    write("robots.txt", f'User-agent: *\nAllow: /\nSitemap: {profile["website"]}sitemap.xml')
    print("Generated structured site content.")


if __name__ == "__main__":
    main()
