(() => {
  'use strict';
  // Enable double-click local-file reviews without a web server.
  // GitHub Pages continues to use the cleaner directory URLs.
  if (location.protocol === 'file:') {
    document.querySelectorAll('a[href]').forEach(anchor => {
      const href = anchor.getAttribute('href');
      if (href && !href.startsWith('#') && !/^[a-z]+:/i.test(href) && href.endsWith('/')) {
        anchor.setAttribute('href', href + 'index.html');
      }
    });
  }
  const header = document.querySelector('.header');
  const nav = document.querySelector('.navigation');
  const toggler = document.querySelector('.mobile-toggle');
  const topButton = document.querySelector('.back-top');
  function updateScroll() {
    header?.classList.toggle('scrolled', scrollY > 10);
    topButton?.classList.toggle('visible', scrollY > 500);
  }
  addEventListener('scroll', updateScroll, { passive: true });
  updateScroll();
  toggler?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggler.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.nav-dropdown > button').forEach(button => {
    button.addEventListener('click', () => {
      const parent = button.parentElement;
      const open = parent.dataset.open !== 'true';
      parent.dataset.open = String(open);
      button.setAttribute('aria-expanded', String(open));
    });
  });
  topButton?.addEventListener('click', () => scrollTo({top: 0, behavior: 'smooth'}));

  // Local filter interaction for gallery and draft service directory.
  document.querySelectorAll('[data-filter-set]').forEach(group => {
    const target = group.dataset.filterSet;
    group.querySelectorAll('button[data-filter]').forEach(button => {
      button.addEventListener('click', () => {
        group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        document.querySelectorAll(`[data-filter-target="${target}"]`).forEach(item => {
          item.classList.toggle('hidden', button.dataset.filter !== 'all' && item.dataset.category !== button.dataset.filter);
        });
      });
    });
  });
  document.querySelectorAll('[data-search]').forEach(input => {
    const target = input.dataset.search;
    const search = () => {
      const q = input.value.trim().toLocaleLowerCase();
      let visible = 0;
      document.querySelectorAll(`[data-search-target="${target}"]`).forEach(item => {
        const matched = item.textContent.toLocaleLowerCase().includes(q);
        item.classList.toggle('hide-by-search', !matched);
        if (matched) visible++;
      });
      const empty = document.querySelector(`[data-search-empty="${target}"]`);
      empty?.classList.toggle('visible', visible === 0);
    };
    input.addEventListener('input', search);
  });

  // Switch between hospital photos and uncropped photo-card posters.
  const galleryTabs = Array.from(document.querySelectorAll('[data-gallery-tab]'));
  const galleryPanels = Array.from(document.querySelectorAll('[data-gallery-panel]'));
  function selectGalleryTab(tab, focus = false) {
    if (!tab) return;
    galleryTabs.forEach(item => {
      const selected = item === tab;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    galleryPanels.forEach(panel => {
      panel.hidden = panel.dataset.galleryPanel !== tab.dataset.galleryTab;
    });
    if (focus) tab.focus();
  }
  galleryTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectGalleryTab(tab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === 'ArrowLeft') next = (index - 1 + galleryTabs.length) % galleryTabs.length;
      if (event.key === 'ArrowRight') next = (index + 1) % galleryTabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = galleryTabs.length - 1;
      selectGalleryTab(galleryTabs[next], true);
    });
  });
  if (location.hash === '#photo-cards') selectGalleryTab(galleryTabs.find(tab => tab.dataset.galleryTab === 'photocards'));
  const dialog = document.querySelector('#gallery-lightbox');
  document.querySelectorAll('[data-lightbox]').forEach(card => {
    card.addEventListener('click', () => {
      if (!dialog) return;
      const image = dialog.querySelector('img');
      image.src = card.dataset.lightbox;
      image.alt = card.dataset.alt || '';
      dialog.querySelector('p').textContent = card.dataset.caption || '';
      dialog.showModal();
    });
  });
  document.querySelector('.dialog-close')?.addEventListener('click', () => dialog?.close());
  dialog?.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });

  // An intentionally local-only appointment request: no data is transmitted or stored.
  document.querySelector('#appointment-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const isBn = document.documentElement.lang === 'bn';
    const rows = [
      isBn ? 'অ্যাপয়েন্টমেন্ট অনুরোধের খসড়া' : 'Appointment request draft',
      `${isBn ? 'নাম' : 'Name'}: ${data.get('patient')}`,
      `${isBn ? 'ফোন' : 'Phone'}: ${data.get('phone')}`,
      `${isBn ? 'বিভাগ' : 'Department'}: ${data.get('department')}`,
      `${isBn ? 'পছন্দের তারিখ' : 'Preferred date'}: ${data.get('date')}`,
      `${isBn ? 'পছন্দের সময়' : 'Preferred time'}: ${data.get('time')}`,
      '',
      isBn ? 'এটি শুধুমাত্র একটি খসড়া। হাসপাতালে কোনো তথ্য পাঠানো হয়নি।' : 'This is only a draft. Nothing has been sent to the hospital.'
    ];
    const output = document.querySelector('#appointment-result');
    output.textContent = rows.join('\n');
    output.hidden = false;
    output.focus();
  });
  document.querySelector('#copy-appointment')?.addEventListener('click', async () => {
    const output = document.querySelector('#appointment-result');
    if (!output || output.hidden) return;
    try { await navigator.clipboard.writeText(output.textContent); } catch(e) { /* Clipboard may be unavailable over insecure localhost */ }
  });
})();
