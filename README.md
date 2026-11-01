# Yufeng (Eric) Wu — Portfolio

Static migration of the November 1, 2026 Webflow export. Existing layouts, styles, interactions, and content are retained.

## Files

- `site/`: complete exported source and assets. Edit these files, not `dist/`.
- `scripts/build.py`: prepares the GitHub Pages site and writes `migration-audit.json`.
- `dist/`: generated output; ignored by Git.
- `.github/workflows/pages.yml`: builds and deploys on pushes to `main` after Pages is enabled.

The original ZIP remains untouched in the parent folder. Source assets remain at exported quality. The build preserves original media referenced by the homepage and its featured project pages; other JPEG/PNG images are limited to 1440 pixels on their longest side, with JPEG quality 75. Shared assets used by featured projects also remain at full quality. Videos are not recompressed. External Webflow asset URLs are rewritten to local exported files when an unambiguous match exists.

## Build and preview

Requires Python 3.13 and Pillow:

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8000 --directory dist
```

Open http://localhost:8000/. HTML pages are available at both exported `.html` paths and directory paths matching the original extensionless Webflow URLs (GitHub Pages adds a trailing slash). The build stops if published files exceed a conservative 1 GB budget.

## GitHub Pages

1. Create an empty GitHub repository and add it as this repository's `origin`.
2. Push `main`.
3. In repository Settings → Pages, choose **GitHub Actions** as the source, then run the deployment workflow if necessary.
4. Review all pages and interactions on the GitHub preview address before changing DNS.
5. When ready to switch, configure `www.yufengwu.com` in Pages and update the domain's DNS using GitHub's instructions. Domain settings have not been changed by this migration.

No Webflow backend is included: forms, search, password protection, and CMS editing need separate solutions if used. Google Fonts, jQuery CDN, embedded video providers, and any unmatched external URLs remain network dependencies; inspect the audit before canceling hosting. `401.html` does not provide real access protection on static hosting.

## Maintenance

- Homepage and featured project order: `site/index.html`, within the thumbnail links.
- Project text and galleries: the corresponding HTML under `site/work/` or `site/research/`.
- Shared styles: `site/css/yufeng-eric-wus-portfolio.webflow.css`.
- Navigation and footer are repeated across pages; update consistently.
- New media: add under `site/images/`, `site/videos/`, or `site/documents/` and reference it from HTML.
- Run the build and inspect `migration-audit.json` after edits. Never commit generated `dist/`.

The resume link missing from the Webflow ZIP was restored using the existing resume PDF in the parent portfolio folder.


