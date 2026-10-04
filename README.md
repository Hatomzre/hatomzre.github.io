# HUANG Yuntong — academic website

An English academic website built with Quarto for GitHub Pages at **https://hatomzre.github.io/**.

## Website

- Five routes: `/`, `/research/`, `/publications/`, `/teaching/`, `/cv/`
- Light and dark reading themes, self-hosted fonts, the supplied real portrait, and selected personal photographs
- Public research, publications, six teaching appointments, academic service, and postdoctoral availability
- HTML CV summary only: **no PDF CV is approved for public distribution**
- Canonical URLs, sitemap, robots file, social metadata, and Person/ProfilePage structured data
- Automatic publishing from `main` through GitHub Actions

## Publish on GitHub

1. Create the public repository **Hatomzre/hatomzre.github.io**. The files inside this project belong at the repository root, including `.github/`; do not upload the outer project folder or the ZIP itself.
2. In **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source.
3. Push the website source to `main`. The included workflow builds, checks, and publishes the website.
4. Wait for **Build and deploy Quarto site** to finish successfully in the Actions tab.
5. Open **https://hatomzre.github.io/** and test navigation and dark mode.

No custom domain or paid hosting is needed for this launch. Google Scholar, ORCID, analytics, and Search Console can be added later by the owner.

## Local build

Use Python 3 and Quarto 1.9.38:

```powershell
python scripts/render_data.py
quarto render
python scripts/validate.py
```

On Windows, `scripts/build.ps1` performs this sequence and stops if any stage fails. Set `QUARTO_BIN` when using a portable Quarto installation. The post-render script aligns the sitemap with the canonical page addresses.

## Update content

- `profile.yml`: identity, graduation, postdoc availability, links, awards, and service
- `publications.bib`: public articles and preprints
- `data/research.yml`: public research summaries and broad interests
- `data/teaching.yml`: teaching appointments, also used by the HTML CV summary
- `data/talks.yml`: selected talks
- Page `.qmd` files: surrounding page copy

The owner maintains their PDF CV separately. **Do not upload it, generate a substitute, or add a download link without new approval.** PDF assets are ignored by Git and blocked by the site validator.

Only chosen web-ready photographs under `assets/images/` are public. The local `figure/` folder, `_site/`, caches, and temporary files are excluded. The real portrait must not be replaced by an AI-generated portrait.

Keep unpublished research details out of the public pages and repository. Content updates and any future disclosure decisions remain with the owner.

## Add a custom domain later

After purchasing and configuring a domain, change `website` in `profile.yml` and `website.site-url` in `_quarto.yml` together. Rebuild to refresh structured metadata, robots, and sitemap addresses. Add the custom domain in GitHub Pages settings, configure DNS, and enable HTTPS after GitHub verifies it.

## Verification

`scripts/validate.py` checks five routes, local links, landmarks, metadata, exact sitemap addresses, PDF exclusion, and the HTML/source research-disclosure boundary. Recheck the live site after its first deployment, including mobile navigation, dark mode, external publication links, and email.
