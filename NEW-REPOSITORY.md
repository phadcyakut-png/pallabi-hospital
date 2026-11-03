# Pallabi Hospital — new repository guide

This is the migrated source for the English/Bangla Pallabi Hospital & Diagnostic Center site.

- `content/hospital.json`: hospital details, Papry Rahman's sole leadership entry, production `website_url` (computed by deployment).
- `content/photocards.json`: the 14 photo cards and bilingual labels.
- `source-images/photocards/`: original photo cards.
- `build.py`: generates the 22 English and 22 Bengali pages.
- `scripts/prepare_images.py`: generates optimized hospital photos and photo-card WebP images.
- `scripts/release_runtime.py`: sets the site URL and generates canonical tags, CNAME, sitemap/robots hints and versioned CSS/JS, then verifies galleries, images and leadership.
- `.github/workflows/deploy.yml`: builds and publishes the site using GitHub Actions.

## Publishing

In GitHub **Settings → Pages**, select **GitHub Actions** as the source.

The action auto-detects your new GitHub username and repository. With no custom domain, it publishes the site at `https://USERNAME.github.io/REPOSITORY/` (or `https://USERNAME.github.io/` for a user-pages repo).

When you connect your own domain, add a GitHub repository **Actions variable** named `CUSTOM_DOMAIN` with a hostname only, such as `hospital.example.org`. In **Settings → Pages → Custom domain**, enter the exact same hostname. The workflow writes a `site/CNAME` marker for portability and configures the canonical URL and sitemap. **When using GitHub Actions publishing, GitHub ignores the CNAME file:** setting **Settings → Pages → Custom domain** is still required. Do not add `https://`, slashes, or a path to this variable.

Connect Cloudflare DNS to GitHub Pages (NOT Cloudflare Pages). For a root domain, use GitHub's four `A` records for `@`, plus a `www` CNAME to `USERNAME.github.io`; initially choose **DNS only** while HTTPS is provisioned. After the domain works, use **Enforce HTTPS** in GitHub Pages.

## Content and safety

- Photo cards may show identifiable newborns, patients or families. Confirm written permission for public website publication, especially information such as birth dates or medical details.
- Check leadership message approval, legal text, current contact details, and whether displayed hospital services are verified before wider promotion.
- Do not edit generated pages under `site/en/` or `site/bn/`; change source code/data instead.
- If a deployment fails, GitHub → **Actions** → newest **Build and publish Pallabi Hospital** run shows the failing step.

For step-by-step DNS values and no-terminal migration, see the separate migration instructions delivered with the original upgrade package.
