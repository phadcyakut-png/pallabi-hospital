#!/usr/bin/env python3
"""Permanent bilingual Pallabi Hospital post-build config and integrity checks.

Run by GitHub Actions; no command line use is required from the site owner.
Usage: python scripts/release_runtime.py configure|finalize|verify
Environment: GITHUB_REPOSITORY=OWNER/REPO, PALLABI_CUSTOM_DOMAIN=example.org (optional)
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'site'
CONFIG = ROOT/'content/hospital.json'
FILENAME = 'pallabi-site-release-v2'
REMOVED_NAMES = (
    'Md Rubel Howlader', 'Md Hasan Al Yakut', 'Md Jalal Uddin',
    'মোঃ রুবেল হাওলাদার', 'মোঃ হাসান আল ইয়াকুত', 'মোঃ জালাল উদ্দিন',
)


def current_domain():
    domain = os.getenv('PALLABI_CUSTOM_DOMAIN', '').strip().lower()
    if not domain:
        return ''
    if '://' in domain or '/' in domain or ':' in domain or not re.fullmatch(
        r'(?=.{4,253}$)[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', domain
    ) or '.' not in domain or '..' in domain:
        raise ValueError('CUSTOM_DOMAIN must be the hostname alone, e.g. www.example.com (no https:// or slashes)')
    return domain


def website_url():
    domain = current_domain()
    if domain:
        return 'https://' + domain
    repository = os.getenv('GITHUB_REPOSITORY', '').strip()
    if repository.count('/') != 1:
        raise ValueError('Missing GITHUB_REPOSITORY (expected OWNER/REPOSITORY)')
    owner, name = repository.split('/')
    if not re.fullmatch(r'[A-Za-z0-9-]+', owner) or not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
        raise ValueError('Invalid GitHub repository name')
    if name.lower() == f'{owner.lower()}.github.io':
        return f'https://{owner.lower()}.github.io'
    return f'https://{owner.lower()}.github.io/{name}'


def configure():
    data = json.loads(CONFIG.read_text(encoding='utf-8'))
    people = data.get('leaders', [])
    assert len(people) == 1 and people[0]['name_en'] == 'Papry Rahman', 'Expected Papry Rahman as sole leader'
    data['website_url'] = website_url()
    data['preview_mode'] = False
    CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Configured production URL:', data['website_url'])


ASSET_RX = re.compile(r'(?P<prefix>\b(?:href|src)=\")(?P<path>[^\"]*?assets/(?P<name>style\.css|app\.js))(?:\?v=[0-9a-fA-F]{6,64})?(?P<suffix>\")')


def finalize():
    url = website_url()
    domain = current_domain()
    favicon = OUT/'assets/style.css'
    javascript = OUT/'assets/app.js'
    if not favicon.is_file() or not javascript.is_file():
        raise FileNotFoundError('The build has not prepared site/assets/style.css and site/assets/app.js')
    versions = {
        'style.css': hashlib.sha256(favicon.read_bytes()).hexdigest()[:16],
        'app.js': hashlib.sha256(javascript.read_bytes()).hexdigest()[:16],
    }
    html_files = list(OUT.rglob('*.html'))
    if len(html_files) < 46:
        raise RuntimeError(f'Expected the bilingual site, found only {len(html_files)} HTML files')
    changed = 0
    for file in html_files:
        raw = file.read_text(encoding='utf-8')
        # Version only the two shared assets. A new HTML page will request the
        # matching CSS/JS even if the browser cached the previous filenames.
        rendered = ASSET_RX.sub(lambda m: f'{m.group("prefix")}{m.group("path")}?v={versions[m.group("name")]}{m.group("suffix")}', raw)
        parts = file.relative_to(OUT).parts
        if len(parts) >= 2 and parts[0] in ('en', 'bn') and parts[-1] == 'index.html':
            slug = '/'.join(parts[:-1])
            canonical = f'{url}/{slug}/'
            # Existing alternate links in build.py are relative and continue to
            # resolve correctly on both default GitHub URLs and custom domains.
            if 'rel="canonical"' in rendered:
                rendered = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>', '', rendered)
            if '<head>' not in rendered:
                raise RuntimeError(f'No HTML head in {file}')
            rendered = rendered.replace('<head>', f'<head><link rel="canonical" href="{html.escape(canonical, quote=True)}"><meta property="og:url" content="{html.escape(canonical, quote=True)}">', 1)
        if rendered != raw:
            file.write_text(rendered, encoding='utf-8')
            changed += 1
    cname = OUT/'CNAME'
    if domain:
        cname.write_text(domain+'\n', encoding='utf-8')
    else:
        cname.unlink(missing_ok=True)
    robots = OUT/'robots.txt'
    robots.write_text('User-agent: *\nAllow: /\nSitemap: '+url+'/sitemap.xml\n', encoding='utf-8')
    if not (OUT/'sitemap.xml').is_file():
        raise RuntimeError('Missing sitemap.xml; configure must run before build.py')
    print(f'Finalized {changed} pages; cache version CSS={versions["style.css"]}, JS={versions["app.js"]}')
    print('Domain:', domain if domain else '(default new GitHub Pages URL)')


class GalleryCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tabs = []
        self.panels = []
        self.poster_buttons = []
        self.hospital_buttons = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('data-gallery-tab'):
            self.tabs.append(a['data-gallery-tab'])
        if a.get('data-gallery-panel'):
            self.panels.append(a['data-gallery-panel'])
        if a.get('data-filter-target') == 'photocards':
            self.poster_buttons.append(a)
        if a.get('data-filter-target') == 'gallery':
            self.hospital_buttons.append(a)


def verify():
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    leaders = cfg['leaders']
    assert len(leaders) == 1 and leaders[0]['name_en'] == 'Papry Rahman', 'Leadership config is not single-person'
    assert cfg.get('website_url') == website_url(), 'Production URL mismatch'
    assert cfg.get('preview_mode') is False, 'Robots must not be in preview mode'
    photo_cfg = ROOT/'content/photocards.json'
    posters = json.loads(photo_cfg.read_text(encoding='utf-8'))
    assert len(posters) == 14 and len({c['file'] for c in posters}) == 14, 'Need 14 unique photocards'
    assert {c['category'] for c in posters} == {'newborn', 'team', 'messages'}, 'Photocard categories incomplete'
    for card in posters:
        stem = Path(card['file']).stem
        assert (ROOT/'source-images/photocards'/card['file']).is_file(), f'Missing source poster {card["file"]}'
        for suffix in ('.webp', '-preview.webp'):
            assert (OUT/'assets/images'/f'{stem}{suffix}').is_file(), f'Missing poster output {stem}{suffix}'
    css_v = hashlib.sha256((OUT/'assets/style.css').read_bytes()).hexdigest()[:16]
    js_v = hashlib.sha256((OUT/'assets/app.js').read_bytes()).hexdigest()[:16]
    for lang in ('en','bn'):
        for slug in ('gallery','leadership','management'):
            page = OUT/lang/slug/'index.html'
            assert page.is_file(), f'Build missing: {page}'
            doc = page.read_text(encoding='utf-8')
            assert f'style.css?v={css_v}' in doc and f'app.js?v={js_v}' in doc, f'{lang}/{slug}: CSS/JS version missing'
            assert f'{website_url()}/{lang}/{slug}/' in doc, f'{lang}/{slug}: canonical missing'
            for removed in REMOVED_NAMES:
                assert removed not in doc, f'Removed person still referenced in {lang}/{slug}: {removed}'
            if slug in ('leadership','management'):
                assert ('Papry Rahman' if lang == 'en' else 'পাপড়ি রহমান') in doc, f'Chairman missing from {lang}/{slug}'
            else:
                parsed = GalleryCheck()
                parsed.feed(doc)
                assert parsed.tabs == ['hospital','photocards'], f'{lang}: gallery tabs broken: {parsed.tabs}'
                assert parsed.panels == ['hospital','photocards'], f'{lang}: gallery panels broken'
                assert len(parsed.poster_buttons) == 14, f'{lang}: expected 14 posters'
                assert len(parsed.hospital_buttons) >= 1, f'{lang}: hospital photos missing'
                assert all(b.get('data-lightbox','').endswith('.webp') for b in parsed.poster_buttons)
                assert all(b.get('data-category') in ('newborn','team','messages') for b in parsed.poster_buttons)
        print(f'PASS {lang}: 14 posters, two gallery tabs, single Chairman, cache-versioned assets')
    for removed in ('CEO.jpeg','Managing Director.jpeg','Director.jpeg'):
        assert not (ROOT/'source-images'/removed).exists(), f'Old portrait source was not removed: {removed}'
    for removed in ('ceo.webp','managing-director.webp','director.webp'):
        assert not (OUT/'assets/images'/removed).exists(), f'Old portrait still published: {removed}'
    domain = current_domain()
    if domain:
        assert (OUT/'CNAME').read_text(encoding='utf-8').strip() == domain, 'CNAME mismatch'
    else:
        assert not (OUT/'CNAME').exists(), 'Unexpected CNAME in default GitHub deployment'
    assert len(list(OUT.rglob('*.html'))) >= 46
    assert (OUT/'sitemap.xml').is_file(), 'Missing sitemap'
    print('PASS: deployment output verified (46+ pages, sitemap, canonical URLs, images, leadership)')


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('configure','finalize','verify'):
        raise SystemExit('Usage: release_runtime.py configure|finalize|verify')
    globals()[sys.argv[1]]()
