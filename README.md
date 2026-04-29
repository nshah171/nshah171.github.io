# nshah.net

Source for [nshah.net](https://nshah.net). Built on [Jekyll + al-folio](https://github.com/alshedivat/al-folio) and deployed via GitHub Actions to GitHub Pages.

Pre-2026 history (the legacy static HTML site) lives in the archived [nshah171/personal-website](https://github.com/nshah171/personal-website) repo.

## How the site is organized

Two source-of-truth files drive most of the content:

- **`_bibliography/papers.bib`** — every publication. Feeds the `/publications/` page.
- **`_data/cv.yml`** — the CV. Feeds *both* the `/cv/` HTML page *and* the downloadable LaTeX PDF (`cv/vita.pdf` → `assets/pdf/cv.pdf`).

These are intentionally separate. New entries always go into `papers.bib` first; once a paper is accepted at a refereed venue, also add a one-line entry to `cv.yml`.

## Common edits

### Add a new paper

1. **Add a BibTeX entry** to `_bibliography/papers.bib`:

   ```bibtex
   @inproceedings{authorYYYYkeyword,
     title         = {Your Paper Title},
     author        = {First Author and Second Author and Neil Shah},
     booktitle     = {Conference Name},
     year          = {2026},
     abbr          = {KDD},                            % short venue badge: KDD, ICLR, NeurIPS, etc.
     pdf           = {https://arxiv.org/pdf/2603.12345},
     arxiv         = {2603.12345},
     preview       = {authorYYYYkeyword.png},          % see step 2
     abstract      = {Full abstract here. Escape \% and balance braces.},
   }
   ```

2. **Drop a preview image** at `assets/img/publication_preview/<bibkey>.png`. Any reasonable size; Jekyll will generate responsive 480/800/1400 WebP variants automatically. Use `placeholder.png` as the value if you don't have art yet.

3. **Optional fields** to enable extras:

   | Field | Effect |
   |---|---|
   | `selected = {true}` | Surfaces the paper in the *Selected Publications* block on the homepage. |
   | `code = {URL}` | Adds a "Code" button next to the entry. URL must be reachable. |
   | `award = {true}` + `award_name = {Best Paper Award}` | Renders a red "Best Paper Award" pill. Use that exact wording. |
   | `battle_tested = {true}` | Renders a green "Battle-Tested" pill — for production-deployed / industrial work. |

   `award` and `battle_tested` can both be set on the same paper (FRAUDAR has both).

4. **If accepted at a refereed venue,** also add it to the CV — see below.

### Update the CV (any aspect)

The CV is generated from a single YAML file: `_data/cv.yml`. Every change — new paper, new talk, intern, award, etc. — is one edit there.

```bash
# Edit the YAML
$EDITOR _data/cv.yml

# Regenerate the LaTeX + PDF and copy to the website's download path
cd cv && make
cp vita.pdf ../assets/pdf/cv.pdf

# Commit both PDF copies + the YAML in the same commit
```

The website's `/cv/` page reads `_data/cv.yml` directly on the next Jekyll rebuild — no extra step.

**Rules:**
- **Refereed publications only** in `cv.yml` — arXiv-only preprints stay in the bib (so they appear on `/publications/`) but not in the CV. Add the CV entry once the paper is accepted at a venue.
- **Don't hand-edit `cv/vita.tex`** — it's regenerated from the YAML on every `make`. Always edit the YAML.

See [`cv/README.md`](cv/README.md) for the YAML schema and Makefile targets.

### Change the homepage / about text

`_pages/about.md` controls the homepage. Two layers:

1. **Frontmatter** controls the chrome around the text:
   - `subtitle` — the line under your name (currently `Director of Research, Senior Principal Scientist at Snap.`).
   - `profile.image`, `profile.more_info` — photo + contact lines.
   - `selected_papers: true` — show/hide the *Selected Publications* block.
   - `announcements.enabled` + `.limit` — the news feed (8 most recent, scrollable).

2. **Body** is plain markdown — rewrite the intro paragraphs freely. Current structure:
   - Paragraph 1: research framing + methods + concrete impact.
   - Paragraph 2: PhD + undergrad + advisors.
   - One-line consulting contact.

Restart Jekyll only if you change frontmatter keys; markdown body changes hot-reload.

## Running locally

```bash
bundle install
bundle exec jekyll serve --port 4002
# http://localhost:4002
```

Auto-regenerates on changes under `_pages/`, `_news/`, `_bibliography/papers.bib`, `_data/`, `_layouts/`, `_includes/`, `_sass/`. `_config.yml` changes require a restart.

**One known gotcha (sass-embedded):** if Jekyll dies during SCSS compile with `"end of file reached"`, run `bundle update sass-embedded`. The 1.97.x binary gets killed on this Mac; 1.99+ works.

## Deploying

Push to `main` → `.github/workflows/deploy.yml` builds the Jekyll site → force-pushes `_site/` to `gh-pages` → live at nshah.net within 3–6 minutes.

```bash
git add <files>
git commit -m "..."
git push origin main
```

Watch the workflow at https://github.com/nshah171/nshah171.github.io/actions.

The `gh-pages` branch is build-output only — never edit it directly. The custom domain is pinned via `CNAME` at the source root, preserved in every build.

## Repo layout (for reference)

```
nshah171.github.io/
├── _bibliography/papers.bib    # all publications
├── _data/cv.yml                # canonical CV (drives /cv/ + the PDF)
├── _news/                      # one markdown file per news item
├── _pages/                     # about, publications, cv, news, 404
├── _layouts/, _includes/, _sass/   # al-folio theme overrides
├── _config.yml                 # site config
├── assets/
│   ├── img/prof_pic.jpg
│   ├── img/publication_preview/<bibkey>.png  # per-paper teasers
│   └── pdf/cv.pdf              # CV download (mirror of cv/vita.pdf)
├── cv/                         # LaTeX CV pipeline (Makefile + build_tex.py)
├── CNAME                       # nshah.net
└── .github/workflows/deploy.yml
```

`CLAUDE.md` captures non-obvious project rules in a form an AI assistant can pick up automatically.
