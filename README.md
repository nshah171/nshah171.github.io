# nshah.net — al-folio version

This is a [Jekyll + al-folio](https://github.com/alshedivat/al-folio) port of
the nshah.net site. It lives alongside the current (static HTML) site at the
repo root and is not yet wired up for deployment.

## Contents

- `_bibliography/papers.bib` — 125 publications (124 from `../publications.html`
  + 1 salvaged from `../../new-personal-website/_data/papers.yml`), each with
  an `abbr`, `year`, `pdf`, and `preview` field for al-folio.
- `_news/` — 106 news items migrated from `../index.html`.
- `_pages/about.md` — biography, ported verbatim from the current site.
- `_pages/publications.md` / `_pages/cv.md` / `_pages/news.md` — site pages.
- `assets/img/publication_preview/` — 89 per-paper PNG teasers reused from
  `../../new-personal-website/assets/images/`, plus a neutral `placeholder.png`
  for the 36 papers still needing art. See [IMAGE_TODO.md](IMAGE_TODO.md).
- `assets/img/prof_pic.jpg` — profile photo (copied from `../images/`).
- `assets/pdf/cv.pdf` — CV (copied from `../cv/vita.pdf`).
- `assets/pdf/*.pdf` — 42 legacy paper PDFs referenced from BibTeX entries.

## Running locally

### Via Docker (al-folio's recommended path, if Docker is available)

```bash
docker compose pull && docker compose up
# open http://localhost:8080
```

On a Snap-managed Mac, Docker Desktop may require an org sign-in; use the
Ruby path below if you hit an auth wall.

### Via Ruby + Bundler

```bash
bundle install
bundle exec jekyll serve
# open http://127.0.0.1:4000
```

Tested locally: builds in ~7s after image cache warms, all four pages
return HTTP 200, 125 publications render with per-paper preview images,
106 news items render.

## Not done in this pass

- **Deployment.** The current site serves from the `gh-pages` branch root;
  this directory is scaffold only. Cutting over means either (a) moving
  these files to the repo root on a new branch and pointing GitHub Pages
  at it, or (b) using GitHub Actions (al-folio upstream ships a workflow).
- **Custom preview images** for the 36 papers flagged in
  [IMAGE_TODO.md](IMAGE_TODO.md) — they show a gradient placeholder for now.
- **Structured CV.** The CV page links to the PDF; al-folio also supports
  RenderCV and JSONResume if you'd prefer a browsable HTML version later.
- **Analytics / GTM / CNAME.** Intentionally omitted so the scaffold doesn't
  affect the live site.
