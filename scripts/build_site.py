#!/usr/bin/env python3
"""Build a small static HTML site for the LLM Wiki.

This intentionally uses only the Python standard library so GitHub Pages can
build the site without package installation.
"""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
CONTENT_ROOTS = ("wiki", "raw")

LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def site_path_for(source: Path) -> Path:
    rel = source.relative_to(ROOT)
    return (SITE / rel).with_suffix(".html")


def display_path(source: Path) -> str:
    rel = source.relative_to(ROOT)
    if rel == Path("wiki/index.md"):
        return "Home"
    return str(rel.with_suffix("")).replace("/", " / ")


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
    title = source.stem.replace("-", " ").title()
    body = render_markdown(source.read_text(encoding="utf-8"))
    nav_items = []
    for file in files:
        href = site_path_for(file).relative_to(SITE)
        nav_items.append(
            f'<a href="/LLM-WIKI/{html.escape(str(href), quote=True)}">'
            f"{html.escape(display_path(file))}</a>"
        )
    nav = "\n".join(nav_items)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · LLM Wiki</title>
  <link rel="stylesheet" href="/LLM-WIKI/assets/site.css">
</head>
<body>
  <aside class="sidebar">
    <a class="brand" href="/LLM-WIKI/wiki/index.html">LLM Wiki</a>
    <nav>{nav}</nav>
  </aside>
  <main class="content">
    <div class="path">{html.escape(str(source.relative_to(ROOT)))}</div>
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
  --bg: #fbfaf7;
  --panel: #f1eee8;
  --text: #24211d;
  --muted: #6d665e;
  --line: #ded8cf;
  --accent: #276b5d;
  --code: #eee9df;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
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
  background: var(--panel);
  padding: 24px 18px;
}

.brand {
  display: block;
  margin-bottom: 20px;
  color: var(--text);
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}

nav {
  display: grid;
  gap: 6px;
}

nav a {
  border-radius: 6px;
  padding: 7px 8px;
  color: var(--muted);
  text-decoration: none;
}

nav a:hover {
  background: rgba(39, 107, 93, 0.08);
  color: var(--accent);
}

.content {
  width: min(100%, 920px);
  padding: 48px 40px 80px;
}

.path {
  margin-bottom: 18px;
  color: var(--muted);
  font-size: 13px;
}

article {
  font-size: 17px;
}

h1, h2, h3, h4, h5, h6 {
  margin: 1.45em 0 0.45em;
  line-height: 1.2;
}

h1 {
  margin-top: 0;
  font-size: 42px;
}

h2 {
  border-top: 1px solid var(--line);
  padding-top: 24px;
  font-size: 26px;
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
  background: var(--panel);
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
  <meta http-equiv="refresh" content="0; url=/LLM-WIKI/wiki/index.html">
  <title>LLM Wiki</title>
  <link rel="canonical" href="/LLM-WIKI/wiki/index.html">
</head>
<body>
  <p><a href="/LLM-WIKI/wiki/index.html">Open LLM Wiki</a></p>
</body>
</html>
"""
    (SITE / "index.html").write_text(html_text, encoding="utf-8")


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
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(files)} pages in {SITE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
