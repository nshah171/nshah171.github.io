#!/usr/bin/env python3
"""Generate vita_generated.tex from ../_data/cv.yml.

Drives the dual-source CV: same YAML powers the al-folio HTML page at /cv/ and
this script emits a LaTeX file in the style of the existing vita.tex so
`pdflatex` produces the PDF.

Inputs:  ../_data/cv.yml
Outputs: vita_generated.tex (sibling of the source vita.tex).
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit(
        "PyYAML not installed. Run: pip install -r requirements.txt "
        "(or pip install pyyaml)"
    )

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
YAML_PATH = os.path.join(SCRIPT_DIR, "..", "_data", "cv.yml")
OUT_PATH = os.path.join(SCRIPT_DIR, "vita.tex")

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

LATEX_SPECIALS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def format_date(d):
    """YYYY-MM or YYYY or 'present' -> 'Month YYYY' or 'YYYY' or 'present'."""
    if d is None:
        return ""
    s = str(d).strip()
    if s.lower() == "present":
        return "present"
    m = re.match(r"^(\d{4})-(\d{1,2})(?:-\d{1,2})?$", s)
    if m:
        year = m.group(1)
        month = int(m.group(2))
        return f"{MONTHS[month - 1]} {year}"
    m = re.match(r"^(\d{4})$", s)
    if m:
        return m.group(1)
    return s


def date_range(start, end):
    s = format_date(start)
    e = format_date(end)
    if s and e:
        return f"{s} - {e}"
    return s or e or ""


def tex_escape(s):
    """Escape LaTeX specials while translating inline markdown to LaTeX.

    Handles:
      - [text](url)  -> \\href{url}{text}
      - **text**     -> \\textbf{text}
      - *text*       -> \\emph{text}
    Then escapes raw specials in any leftover literal text.
    """
    if s is None:
        return ""
    s = str(s)

    placeholders = {}

    def stash(tex):
        key = f"\x00PH{len(placeholders)}\x00"
        placeholders[key] = tex
        return key

    # Markdown link -> \href{url}{text}
    def sub_link(m):
        text, url = m.group(1), m.group(2)
        # escape url minimally (preserve special href chars)
        url_escaped = url.replace("%", r"\%").replace("#", r"\#")
        # text is still markdown-ish; leave the already-placeholderized stashes untouched
        text_escaped = _escape_plain(text)
        return stash(f"\\href{{{url_escaped}}}{{{text_escaped}}}")

    # Markdown bold -> \textbf{...}
    def sub_bold(m):
        return stash(f"\\textbf{{{_escape_plain(m.group(1))}}}")

    # Markdown italic -> \emph{...}
    def sub_em(m):
        return stash(f"\\emph{{{_escape_plain(m.group(1))}}}")

    # apply in order: links first (they may contain nested bold), then bold, then italic
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", sub_link, s)
    s = re.sub(r"\*\*([^*]+)\*\*", sub_bold, s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", sub_em, s)

    # escape the remaining literal text (preserves placeholders because \x00 isn't a special)
    s = _escape_plain(s)

    # restore placeholders
    for k, v in placeholders.items():
        s = s.replace(k, v)
    return s


def _escape_plain(s):
    """Escape raw LaTeX specials in a chunk of literal text."""
    # escape backslash first but leave placeholders alone
    out = []
    for ch in s:
        if ch == "\x00":
            out.append(ch)
        elif ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in LATEX_SPECIALS:
            out.append(LATEX_SPECIALS[ch])
        else:
            out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_education(entries):
    lines = [r"\section*{\bf \textsc{Education}}", r"\vspace{-5mm}\HRule", r"\begin{itemize}"]
    for e in entries:
        degree = e.get("degree", "")
        area = e.get("area", "")
        institution = e.get("institution", "")
        dates = date_range(e.get("start_date"), e.get("end_date"))
        line = f"\\item \\textbf{{{tex_escape(degree)}}}: {tex_escape(area)}, {tex_escape(institution)}"
        if dates:
            line += f", {tex_escape(dates)}"
        if e.get("highlights"):
            hl = ".  ".join(tex_escape(h) for h in e["highlights"])
            # ensure trailing period for sentence flow
            if not hl.endswith("."):
                hl += "."
            line += f" \\\\\n{hl}"
        lines.append(line)
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def render_experience(entries):
    lines = [r"\section*{\bf \textsc{Positions}}", r"\vspace{-5mm}\HRule", r"\begin{itemize}"]
    for e in entries:
        company = tex_escape(e.get("company", ""))
        position = tex_escape(e.get("position", ""))
        dates = date_range(e.get("start_date"), e.get("end_date"))
        parts = [f"\\item {{\\bf {company}}}"]
        if position:
            parts.append(f", {position}")
        parts.append(".")
        if e.get("highlights"):
            hl = ".  ".join(tex_escape(h) for h in e["highlights"])
            if not hl.endswith("."):
                hl += "."
            parts.append(f" \\\\ {hl}")
        if dates:
            parts.append(f" \\\\ {tex_escape(dates)}")
        lines.append("".join(parts))
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def render_bullet_list(entries, *, numbered=False):
    """Generic bullet list. Supports entries with `bullet` key or inline strings."""
    env = "etaremune" if numbered else "itemize"
    opts = "[itemsep=1pt,parsep=0pt]" if numbered else ""
    lines = [f"\\begin{{{env}}}{opts}"]
    for e in entries:
        if isinstance(e, dict) and "bullet" in e:
            text = tex_escape(e["bullet"])
        else:
            text = tex_escape(e)
        lines.append(f"\\item {text}")
    lines.append(f"\\end{{{env}}}")
    return "\n".join(lines)


def render_skills(entries):
    lines = [r"\section*{\bf \textsc{Technical Skills}}", r"\vspace{-5mm}\HRule", r"\begin{itemize}"]
    for e in entries:
        name = tex_escape(e.get("name", ""))
        kws = e.get("keywords", []) or []
        kw_text = ", ".join(tex_escape(k) for k in kws)
        lines.append(f"\\item \\emph{{{name}}}: {kw_text}")
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

PUBLICATION_SECTIONS = {
    "Refereed Conference Publications",
    "Refereed Journal Publications",
    "Refereed Workshop Publications",
    "Surveys",
    "Tutorials",
    "Book Chapters",
}

# Sections that should appear grouped under "Academic Experience"
ACADEMIC_SECTIONS_ORDER = [
    "Invited Talks",
    "Service — Conference Organization",
    "Service — Peer Review",
    "Mentorship — Internships and Student Advisory Roles",
    "Mentorship — Thesis Supervision",
    "Funding",
    "Teaching",
]


def render_section(title, entries):
    if title == "Education":
        return render_education(entries)
    if title == "Experience":
        return render_experience(entries)
    if title == "Skills":
        return render_skills(entries)
    if title == "Summary":
        # Print as prose paragraph(s), not a list, since the original vita.tex
        # had no Summary section header. Skip to avoid duplicating the header.
        return ""
    # generic — includes Awards, all publication sub-sections, service, talks, etc.
    return render_bullet_list(entries, numbered=(title in PUBLICATION_SECTIONS))


def split_grouped(title):
    """'Service — Peer Review' -> ('Service', 'Peer Review')."""
    if " — " in title:
        a, b = title.split(" — ", 1)
        return a, b
    return None, title


def emit_preamble(cv):
    name = cv.get("name", "")
    label = cv.get("label", "Director of Research, Senior Principal Scientist")
    # extract summary text if present
    summary_block = ""
    sections = cv.get("sections") or {}
    summary = sections.get("Summary") or []
    if summary:
        # support either [ "text" ] or [ {bullet: "text"} ]
        texts = []
        for s in summary:
            if isinstance(s, dict) and "bullet" in s:
                texts.append(s["bullet"])
            else:
                texts.append(str(s))
        # first entry is the "label" under the name in the header; treat as job title
        # we keep the header minimalist like the original vita.tex
        summary_block = " ".join(texts)

    email = cv.get("email", "")
    location = cv.get("location", "")

    preamble = r"""\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage[total={6.5in, 9in}]{geometry}
\newcommand{\HRule}{\rule{\linewidth}{0.5mm}}
\setlength{\parindent}{1pc}
\usepackage[linktocpage]{hyperref}
\usepackage{enumitem}
\setlist[itemize]{noitemsep}
\usepackage{etaremune}
\usepackage{libertine}

\def\name{\textrm{{""" + tex_escape(name) + r"""}}}

\markright{\name}
\thispagestyle{empty}

\begin{document}

{\Huge \bf \textsc{\name}}

\vspace{0.25in}
\begin{tabular}[t]{cc}
 \begin{minipage}[t,left]{0.5\linewidth}
 """ + tex_escape(label.split(" at ")[0] if " at " in label else label) + r""" \\
 \href{http://www.snap.com}{Snap Inc.} \\
 """ + tex_escape(location) + r"""
 \end{minipage} \hfill \quad \quad \quad \quad \quad \quad \quad \begin{minipage}[t,right]{0.5\linewidth}
  Email: \texttt{{\fontfamily{pcr}\selectfont """ + tex_escape(email.replace('@', '[at]').replace('.', '[dot]')) + r"""}}\\
  Last Update: \today
\end{minipage}
\end{tabular} \\
"""
    return preamble


def emit_body(cv):
    sections = cv.get("sections") or {}
    parts = []

    def emit_top(title, content):
        parts.append(content)

    # Education, Experience, Awards first
    for key in ["Education", "Experience", "Awards and Distinctions"]:
        if key in sections:
            if key == "Awards and Distinctions":
                parts.append(r"\section*{\bf \textsc{Awards \& Distinctions}}")
                parts.append(r"\vspace{-5mm}\HRule")
                parts.append(render_bullet_list(sections[key]))
            else:
                parts.append(render_section(key, sections[key]))

    # Publications block: one top-level section + subsections
    pub_keys_present = [k for k in PUBLICATION_SECTIONS if k in sections]
    if pub_keys_present:
        # preserve insertion order from the yaml
        ordered = [k for k in sections.keys() if k in PUBLICATION_SECTIONS]
        parts.append(r"\section*{\bf \textsc{Publications}}")
        parts.append(r"\vspace{-5mm}\HRule")
        for sub in ordered:
            parts.append(r"\subsection*{\bf {" + tex_escape(sub.replace("Refereed ", "")) + r"}}")
            parts.append(render_bullet_list(sections[sub], numbered=True))

    # Academic Experience block: group talks, service, mentorship, funding, teaching
    acad_keys_present = [k for k in ACADEMIC_SECTIONS_ORDER if k in sections]
    if acad_keys_present:
        parts.append(r"\section*{\bf \textsc{Academic Experience}}")
        parts.append(r"\vspace{-5mm}\HRule")
        last_group = None
        for key in acad_keys_present:
            group, sub = split_grouped(key)
            if group and group != last_group:
                parts.append(r"\subsection*{\bf {" + tex_escape(group) + r"}}")
                last_group = group
                parts.append(r"\subsubsection*{\bf {" + tex_escape(sub) + r"}}")
                parts.append(render_bullet_list(sections[key]))
            elif group and group == last_group:
                parts.append(r"\subsubsection*{\bf {" + tex_escape(sub) + r"}}")
                parts.append(render_bullet_list(sections[key]))
            else:
                # top-level (Funding, Teaching, Invited Talks)
                parts.append(r"\subsection*{\bf {" + tex_escape(sub) + r"}}")
                parts.append(render_bullet_list(sections[key]))
                last_group = None

    # Skills
    if "Skills" in sections:
        parts.append(render_section("Skills", sections["Skills"]))

    # References (static, matches original vita.tex)
    parts.append(r"\section*{\bf \textsc{References}}")
    parts.append(r"\vspace{-5mm}\HRule")
    parts.append(r"\vspace{1em}")
    parts.append(r"Available upon request.")
    parts.append(r"\bigskip")
    parts.append(r"\end{document}")

    return "\n\n".join(parts)


def main():
    with open(YAML_PATH) as f:
        data = yaml.safe_load(f)
    cv = data.get("cv") or {}
    if not cv:
        sys.exit(f"no `cv:` root key found in {YAML_PATH}")

    tex = emit_preamble(cv) + "\n" + emit_body(cv)
    with open(OUT_PATH, "w") as f:
        f.write(tex)
    print(f"wrote {OUT_PATH}  ({len(tex)} chars)")


if __name__ == "__main__":
    main()
