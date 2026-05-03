#!/usr/bin/env python3
"""Build a small static HTML site for the LLM Wiki.

This intentionally uses only the Python standard library so GitHub Pages can
build the site without package installation.
"""

from __future__ import annotations

import html
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
CONTENT_ROOTS = ("wiki", "raw")
NAV_ROOT = "wiki"

LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def site_path_for(source: Path) -> Path:
    rel = source.relative_to(ROOT)
    return (SITE / rel).with_suffix(".html")


def href_from(source: Path, target: Path) -> str:
    source_dir = site_path_for(source).parent
    return os.path.relpath(target, source_dir).replace(os.sep, "/")


def page_title(source: Path) -> str:
    rel = source.relative_to(ROOT)
    if rel == Path("wiki/index.md"):
        return "Wiki Index"
    text = source.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return source.stem.replace("-", " ").title()


def nav_group(source: Path) -> str:
    rel = source.relative_to(ROOT)
    if rel == Path("wiki/index.md"):
        return "Start"
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "wiki":
        return parts[1].replace("-", " ").title()
    return parts[0].replace("-", " ").title()


def render_nav(files: list[Path], current: Path) -> str:
    nav_files = [
        file
        for file in files
        if file.relative_to(ROOT).parts[0] == NAV_ROOT
    ]
    nav_files.sort(key=lambda file: (nav_group(file), page_title(file)))

    groups: dict[str, list[Path]] = {}
    for file in nav_files:
        groups.setdefault(nav_group(file), []).append(file)

    ordered_groups = sorted(groups)
    if "Start" in ordered_groups:
        ordered_groups.remove("Start")
        ordered_groups.insert(0, "Start")

    sections: list[str] = []
    for group in ordered_groups:
        links = []
        for file in groups[group]:
            href = site_path_for(file).relative_to(SITE)
            active = " active" if file == current else ""
            links.append(
                f'<a class="nav-link{active}" href="{html.escape(href_from(current, SITE / href), quote=True)}">'
                f"{html.escape(page_title(file))}</a>"
            )
        sections.append(
            '<section class="nav-section">'
            f'<div class="nav-heading">{html.escape(group)}</div>'
            f'{"".join(links)}'
            '</section>'
        )

    return "\n".join(sections)


def convert_link(target: str) -> str:
    if "://" in target or target.startswith("#") or target.startswith("mailto:"):
        return target

    path, sep, fragment = target.partition("#")
    if path.endswith(".md"):
        path = str(Path(path).with_suffix(".html"))
    return path + (sep + fragment if sep else "")


def render_inline(text: str) -> str:
    placeholders: list[str] = []

    def stash_code(match: re.Match[str]) -> str:
        placeholders.append(f"<code>{html.escape(match.group(1))}</code>")
        return f"\x00{len(placeholders) - 1}\x00"

    escaped = html.escape(INLINE_CODE_RE.sub(stash_code, text))

    def link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        href = html.escape(convert_link(match.group(2)), quote=True)
        return f'<a href="{href}">{label}</a>'

    escaped = LINK_RE.sub(link, escaped)

    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"\x00{index}\x00", value)

    return escaped


def render_table(rows: list[str]) -> str:
    parsed = [row.strip().strip("|").split("|") for row in rows]
    parsed = [[cell.strip() for cell in row] for row in parsed]
    header = parsed[0]
    body = parsed[2:] if len(parsed) > 1 else []

    out = ["<table>", "<thead><tr>"]
    out.extend(f"<th>{render_inline(cell)}</th>" for cell in header)
    out.append("</tr></thead>")
    if body:
        out.append("<tbody>")
        for row in body:
            out.append("<tr>")
            out.extend(f"<td>{render_inline(cell)}</td>" for cell in row)
            out.append("</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


def render_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_rows: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            out.append("<ul>")
            out.extend(f"<li>{render_inline(item)}</li>" for item in list_items)
            out.append("</ul>")
            list_items.clear()

    def flush_table() -> None:
        if table_rows:
            out.append(render_table(table_rows))
            table_rows.clear()

    for line in lines:
        if line.startswith("```"):
            if in_code:
                klass = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                code = html.escape("\n".join(code_lines))
                out.append(f"<pre><code{klass}>{code}</code></pre>")
                in_code = False
                code_lang = ""
                code_lines.clear()
            else:
                flush_paragraph()
                flush_list()
                flush_table()
                in_code = True
                code_lang = line.strip("`").strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        if line.startswith("|"):
            flush_paragraph()
            flush_list()
            table_rows.append(line)
            continue

        flush_table()

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            continue

        item = re.match(r"^-\s+(.+)$", line)
        if item:
            flush_paragraph()
            list_items.append(item.group(1))
            continue

        flush_list()
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    flush_table()

    return "\n".join(out)


def render_page(source: Path, files: list[Path]) -> str:
    title = page_title(source)
    body = render_markdown(source.read_text(encoding="utf-8"))
    nav = render_nav(files, source)
    rel_source = source.relative_to(ROOT)
    source_kind = "Source" if rel_source.parts[0] == "raw" else "Wiki"
    home_href = href_from(source, SITE / "wiki" / "index.html")
    css_href = href_from(source, SITE / "assets" / "site.css")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · LLM Wiki</title>
  <link rel="stylesheet" href="{html.escape(css_href, quote=True)}">
</head>
<body>
  <aside class="sidebar">
    <div class="brand-block">
      <a class="brand" href="{html.escape(home_href, quote=True)}">LLM Wiki</a>
      <div class="tagline">Curated notes and source-backed knowledge.</div>
    </div>
    <nav>{nav}</nav>
  </aside>
  <main class="content">
    <header class="page-header">
      <div class="eyebrow">{html.escape(source_kind)} · {html.escape(str(rel_source))}</div>
    </header>
    <article>
{body}
    </article>
  </main>
</body>
</html>
"""


def write_css() -> None:
    css = """
:root {
  color-scheme: light;
  --bg: #fcfcfb;
  --sidebar: #f5f3ef;
  --surface: #ffffff;
  --text: #1f2523;
  --muted: #6c746f;
  --faint: #929a95;
  --line: #e3e0d8;
  --accent: #16695f;
  --accent-soft: #e6f1ee;
  --code: #f0eee8;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.65;
}

a {
  color: var(--accent);
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
  border-right: 1px solid var(--line);
  background: var(--sidebar);
  padding: 30px 22px;
}

.brand-block {
  margin-bottom: 30px;
}

.brand {
  display: block;
  color: var(--text);
  font-size: 22px;
  font-weight: 700;
  text-decoration: none;
}

.tagline {
  margin-top: 8px;
  max-width: 220px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.45;
}

nav {
  display: grid;
  gap: 22px;
}

.nav-section {
  display: grid;
  gap: 4px;
}

.nav-heading {
  margin-bottom: 5px;
  color: var(--faint);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nav-link {
  border-radius: 8px;
  padding: 8px 10px;
  color: var(--muted);
  font-size: 15px;
  font-weight: 520;
  line-height: 1.35;
  text-decoration: none;
}

.nav-link:hover,
.nav-link.active {
  background: var(--accent-soft);
  color: var(--accent);
}

.content {
  width: min(100%, 980px);
  padding: 64px 56px 96px;
}

.page-header {
  margin-bottom: 14px;
}

.eyebrow {
  color: var(--faint);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

article {
  max-width: 820px;
  font-size: 17px;
}

h1, h2, h3, h4, h5, h6 {
  margin: 1.45em 0 0.45em;
  line-height: 1.2;
}

h1 {
  margin-top: 0;
  margin-bottom: 22px;
  font-size: 44px;
  letter-spacing: 0;
}

h2 {
  border-top: 1px solid var(--line);
  margin-top: 44px;
  padding-top: 28px;
  font-size: 25px;
}

p {
  margin: 0 0 18px;
}

ul {
  margin: 12px 0 22px;
  padding-left: 24px;
}

li + li {
  margin-top: 7px;
}

code {
  border-radius: 5px;
  background: var(--code);
  padding: 0.12em 0.32em;
  font-size: 0.9em;
}

pre {
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--code);
  padding: 14px 16px;
}

pre code {
  padding: 0;
  background: transparent;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

th, td {
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}

th {
  background: var(--sidebar);
}

@media (max-width: 760px) {
  body {
    display: block;
  }

  .sidebar {
    position: relative;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .content {
    padding: 32px 20px 56px;
  }

  h1 {
    font-size: 34px;
  }
}
"""
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "site.css").write_text(css.strip() + "\n", encoding="utf-8")


def write_redirect_index() -> None:
    html_text = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=wiki/index.html">
  <title>LLM Wiki</title>
  <link rel="canonical" href="wiki/index.html">
</head>
<body>
  <p><a href="wiki/index.html">Open LLM Wiki</a></p>
</body>
</html>
"""
    (SITE / "index.html").write_text(html_text, encoding="utf-8")


def copy_raw_assets() -> int:
    count = 0
    for source in (ROOT / "raw").rglob("*"):
        if not source.is_file() or source.suffix == ".md":
            continue
        if any(part.startswith(".") for part in source.relative_to(ROOT).parts):
            continue
        target = SITE / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        count += 1
    return count


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    files: list[Path] = []
    for root in CONTENT_ROOTS:
        files.extend(sorted((ROOT / root).rglob("*.md")))

    for source in files:
        target = site_path_for(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(source, files), encoding="utf-8")

    write_css()
    write_redirect_index()
    asset_count = copy_raw_assets()
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(files)} pages and copied {asset_count} raw assets in {SITE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
