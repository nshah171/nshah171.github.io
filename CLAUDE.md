@AGENTS.md

# Personal site (nshah.net) — project rules

Conventions specific to this repo, on top of the al-folio defaults inherited via `@AGENTS.md` above.

## Sources of truth

| Surface | Source file | Audience |
|---|---|---|
| `/publications/` page | `_bibliography/papers.bib` (BibTeX) | All papers — refereed and preprints |
| `/cv/` HTML page **and** `cv/vita.pdf` | `_data/cv.yml` (YAML) → `cv/build_tex.py` → `cv/vita.tex` → `pdflatex` → `cv/vita.pdf` → copy to `assets/pdf/cv.pdf` | Refereed publications only |

The two are **separate sources of truth** by design. A paper is added to the bib first; once it's accepted at a refereed venue, it is *also* added to `cv.yml`. Don't try to derive one from the other.

## CV rules

- **Refereed-only.** Add to `_data/cv.yml` only when the paper has conference/journal acceptance. arXiv-only preprints stay in the bib (so they appear on `/publications/`) but are deliberately excluded from the CV.
  - Exception: surveys and position papers occasionally listed under `Surveys:` even if arXiv-only — that predates the rule.
- **Email is personal:** `nshah171@gmail.com`, never the Snap address. The build script obfuscates it as `nshah171[at]gmail[dot]com` in the LaTeX output.
- **Don't hand-edit `cv/vita.tex`** — it's regenerated from the YAML on every `make`. Edit the YAML.
- **Regenerating the PDF:** `cd cv && make`. This rebuilds `cv/vita.tex` then `cv/vita.pdf`. Then `cp cv/vita.pdf assets/pdf/cv.pdf` so the website's CV download link picks it up. Commit both PDF copies in the same commit.

## Publications page rules

- **No public citation metrics.** Don't enable `altmetric`, `dimensions`, `google_scholar`, or `inspirehep` badges in `_config.yml`. Don't add per-paper citation counters. The publications page links to Google Scholar in its intro for anyone who wants citation counts.
- **Award pills are two distinct kinds:**
  - `award = {true}` + `award_name = {Best Paper Award}` → red pill, "Best Paper Award" (use that exact wording — don't paraphrase as "Best Paper" or "Honorable Mention" etc.).
  - `battle_tested = {true}` → green pill, "Battle-Tested" — for production-deployed / industrial work.
  - Both can coexist on the same entry (FRAUDAR has both).
- **Selected papers** carry `selected = {true}` and surface on the homepage's *Selected Publications* block — a curated cross-section of graph ML, generative recommendation, LLM-based user modeling, and trust & safety.
- **Code buttons** render automatically when an entry has `code = {URL}`. al-folio's `_layouts/bib.liquid` handles this — no template changes needed.
- **Preview images** live at `assets/img/publication_preview/<bibkey>.png`. Jekyll-imagemagick auto-generates responsive 480/800/1400 WebP variants. Default is `placeholder.png` if no custom preview.

## Editing prose

- For about-page / page-description rewrites, **make incremental sentence-level edits** to existing prose, not wholesale rewrites. Preserve structure and voice; surgically replace the disjointed parts.
- When the user supplies a specific draft sentence (e.g. an impact statement), treat it as near-final — light polish only, don't reframe from scratch.

## Local development

```bash
bundle exec jekyll serve --port 4002
# http://localhost:4002
```

Auto-regenerates on changes to `_pages/`, `_news/`, `_bibliography/papers.bib`, `_data/`, `_layouts/`, `_includes/`, `_sass/`. Edits to `_config.yml` require a restart.

**sass-embedded gotcha:** if Jekyll dies during SCSS compile with `"end of file reached"`, run `bundle update sass-embedded`. The 1.97.x binary gets SIGKILL'd on this Mac; 1.99+ works.

## Deploy

- **Push to `main`** → `.github/workflows/deploy.yml` builds Jekyll → force-pushes `_site/` to `gh-pages` → live at `nshah.net` in 3–6 min.
- `gh-pages` is build-output only — never edit it manually.
- `CNAME` lives at the source root (`nshah.net`); preserved in every build via Jekyll's auto-copy of source-root files plus `keep_files: [CNAME, .nojekyll]` in `_config.yml`.
- The legacy site lives at the archived `nshah171/personal-website` repo. This repo is the live source.

## Adding things — quick reference

- **New paper:** add a BibTeX entry to `_bibliography/papers.bib`. Drop a preview image at `assets/img/publication_preview/<bibkey>.png`. If accepted at a refereed venue, also add a one-line `- bullet:` entry under the right subsection of `_data/cv.yml` and rebuild the CV PDF.
- **New news item:** create `_news/announcement_YYYY-MM-DD_N.md` with the standard frontmatter. Homepage feed shows the most recent 8.
- **CV change (any field):** edit `_data/cv.yml` only. The HTML page picks it up automatically; the PDF needs `cd cv && make` and a copy to `assets/pdf/cv.pdf`.
- **About page:** `_pages/about.md`. Subtitle = role + Snap link. Body paragraph 1 leads with the unifying tagline ("modeling users, content, and their interactions at scale") + methods + concrete impact.

## Known intentional surprises

- `cv/vita.log`, `cv/vita.aux`, `cv/vita.out` are tracked from the initial commit but are LaTeX build artifacts. They show up in `git status` after every `make`. Either commit the noise or `git rm --cached` them and add to `.gitignore` — both are valid cleanups.
- jekyll-scholar's bibtex parser silently drops entries whose abstract has malformed escaping (e.g., `\}\{` from a partially-stripped `\href{}{}`). If a paper is missing from `/publications/`, suspect the abstract field first — the build log warns with `Lexer: unexpected token` at a character offset.
