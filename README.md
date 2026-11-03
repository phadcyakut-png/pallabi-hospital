# Pallabi Hospital & Diagnostic Center — Public Website

A bilingual (বাংলা/English), responsive, multi-page static website for **Pallabi Hospital & Diagnostic Center**, Dhaka. This project uses the hospital-provided photographs, logo and Chairman portrait.

## Website contents

- **22 public pages per language** under `/bn/` and `/en/`, plus the root language redirect and custom 404 page.
- Home, About, Vision/Mission, **Management Body**, **Leadership**, Services/Departments, Diagnostics, Facilities, Inpatient, Outpatient, Health Packages, Appointment Enquiries, Gallery, News, Health Insights, Patient Guide, FAQ, Careers, Contact and legal/accessibility pages.
- The previous **Doctors directory has been removed** and can be restored later if approved doctor details become available.
- Home hero contains the **official hospital logo**, with an icon linking to Google Maps.
- Leadership and Management Body pages show only Papry Rahman, the Chairman, with her portrait and message. Her message is **drafted website copy requiring her approval before publication as a personal statement**.
- Contact page contains an embedded Google map, direct Google Maps link, telephone dial action and email link.
- Health-package enquiry cards link to the phone dialer (`tel:`). This is an enquiry interface, not a confirmed list of active packages or prices.
- Appointments are handled by telephone. **No booking form collects patient details.**

## Hospital information currently configured

- **Google Maps address:** R9C8+84J, Road No. 4, Dhaka 1216, Bangladesh
- **Telephone numbers:** 01334-923810 and 01334-923811 (both active `tel:` links throughout the site)
- **Email:** pallabihospital@gmail.com
- **Leadership:** Papry Rahman (Chairman)

The telephone numbers were confirmed by the site owner. Operating hours, departments and services have not been independently confirmed; pages direct visitors to phone the hospital where appropriate.

## Technical approach

This is a **dependency-free Python static-site generator**. It produces HTML, CSS and JavaScript into the `site/` folder. It does not use Astro or require a server/backend. It is suited to GitHub Pages and is portable to other static hosting.

**Project layout**

```text
build.py                   Static HTML generator
content/hospital.json      Editable hospital contacts, leadership and location
content/policies.json      Final-release Privacy, Terms and Accessibility content (EN/BN)
site/                     Deployable generated website
site/en/                  English pages
site/bn/                  Bengali pages
site/assets/              Styles, scripts, optimized photographs and logo
source-images/             Original provided photos and portrait assets
scripts/prepare_images.py  Rebuild the optimized image assets
.github/workflows/deploy.yml  GitHub Actions workflow
CONTENT_TODO.md           Content approvals and outstanding details
QA_REPORT.md              Build and link validation
```

## Preview on a computer

Extract the ZIP and open `site/index.html`, or start a static server:

```bash
cd site
python -m http.server 8000
```

Visit `http://localhost:8000/` in your browser. The primary language is Bengali, with an English switch in the header. In offline mode, the Google Maps embedded frame may require internet access, but the external Maps link remains available.

## Build / update

1. Edit institutional details, numbers, map link, names and the leadership message copy in `content/hospital.json`.
2. Edit other page content or translations within `build.py`. Policy/terms/accessibility text lives in `content/policies.json`. Keep both language versions aligned.
3. Generate all website pages:

```bash
python build.py
```

All HTML pages are regenerated; **do not directly edit a generated `site/en/.../index.html` file** because the next build will overwrite it. Custom styling resides in `site/assets/style.css` and interactivity in `site/assets/app.js`.

To replace/add photographs, put originals in `source-images/`, adjust the paths/image references in `build.py` and regenerate image assets (Pillow required):

```bash
pip install Pillow==11.3.0
python scripts/prepare_images.py
python build.py
```

## Deploy with GitHub Pages

1. Create a new GitHub repository (for example `pallabi-hospital`).
2. Upload the **complete project ZIP contents** so that `build.py`, `site/`, and `.github/workflows/deploy.yml` are at the repository root.
3. Commit and push to the `main` branch.
4. In **GitHub > Repository Settings > Pages**, choose **GitHub Actions** as the build/deployment source.
5. The provided workflow prepares assets, builds the site and publishes the `site/` folder automatically.
6. Check the resulting `username.github.io/repository/` website, especially language navigation, phones, image loading and maps.

### Adding a custom domain

1. Buy the domain and add it under **GitHub Settings > Pages > Custom domain**.
2. Set the DNS records required by GitHub Pages for the chosen apex/subdomain.
3. Enable HTTPS once GitHub has issued the certificate.
4. Enter your complete production URL (for example `https://your-actual-domain.example`, replacing the example) into `website_url` in `content/hospital.json` and rebuild. When this is set, the build will generate `site/sitemap.xml` with absolute URLs.
5. Confirm that GitHub Pages has persisted the chosen domain configuration. If a CNAME file is required by your deployment method, include it in the published `site/` folder; do not add a fake domain now.

## Clinic-specific limitations

This website **does not** currently support real-time doctor schedules, online confirmed appointments, patient portals, billing, medical records or test report access. Do not represent unverified specialties or screening packages as confirmed offerings. For pricing and appointment enquiries, patients are sent directly to the hospital phone number.

No website can be fully institutionally approved solely through code. Before public rollout, the hospital should approve: the leadership messages, signboard phone list, photographs/portrait publishing rights, business address, visitor hours, specialty/test catalog, package titles/availability and legal wording. See `CONTENT_TODO.md`.

## Policy pages and homepage alignment

The **Privacy Policy**, **Terms & Conditions**, and **Accessibility** pages contain fully formatted, visitor-facing English and Bangla content with section navigation and contact details. They are edited in `content/policies.json` and styled in `site/assets/style.css`. The homepage logo is centered within a concentric circular background at desktop and mobile sizes.

The hospital should have its privacy and legal text reviewed before publication to confirm that the published statements match actual record-handling and operational practice.
