/**
 * layout_check.js - Ukur hal yang tidak dicek axe: reflow, zoom, skip link, target size.
 *
 * Dipanggil oleh scripts/check_layout.py:
 *   node scripts/layout_check.js <urls-file> <output-dir> [concurrency]
 *
 * Satu kali load per URL; viewport diubah di halaman yang sama untuk 320px dan 640px
 * (setara zoom 200% pada 1280px).
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const CHROME_CANDIDATES = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
];

function findChrome() {
  const fromEnv = process.env.CHROME_PATH;
  if (fromEnv && fs.existsSync(fromEnv)) return fromEnv;
  return CHROME_CANDIDATES.find(p => fs.existsSync(p));
}

function slug(url, index) {
  const safe = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]+/g, '_').slice(0, 80);
  return `${String(index).padStart(4, '0')}_${safe}`;
}

const MEASURE = () => {
  const vw = window.innerWidth;
  const de = document.documentElement;
  const scroller = Math.max(de.scrollWidth, document.body ? document.body.scrollWidth : 0);

  const offenders = [];
  if (scroller > vw + 2) {
    const limit = Math.min(scroller, vw * 4);
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.right > vw + 2) {
        const cs = getComputedStyle(el);
        if (cs.position === 'fixed') continue;
        offenders.push({
          tag: el.tagName.toLowerCase(),
          cls: (el.className && String(el.className).slice(0, 60)) || '',
          right: Math.round(r.right),
          width: Math.round(r.width),
        });
        if (offenders.length >= 5) break;
      }
    }
  }

  const focusables = Array.from(document.querySelectorAll(
    'a[href], button, input:not([type="hidden"]), select, textarea, [tabindex], iframe'
  )).filter(el => !el.disabled);
  const positiveTabindex = focusables.filter(el => parseInt(el.getAttribute('tabindex') || '0', 10) > 0);
  const firstFocusable = focusables[0];

  let skipLink = null;
  for (const a of Array.from(document.querySelectorAll('a[href^="#"]')).slice(0, 5)) {
    const id = a.getAttribute('href').slice(1);
    if (a.offsetParent !== null && (!id || document.getElementById(id))) {
      skipLink = { text: (a.textContent || '').trim().slice(0, 60), target: id || '(kosong)' };
      break;
    }
  }

  const smallTargets = [];
  const focusRects = [];
  for (const el of focusables) {
    const tag = el.tagName.toLowerCase();
    if (['a', 'button', 'input', 'select', 'textarea'].indexOf(tag) === -1) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    focusRects.push({ x: r.left + r.width / 2, y: r.top + r.height / 2 });
    if (r.width < 24 || r.height < 24) {
      smallTargets.push({
        tag,
        cls: (el.className && String(el.className).slice(0, 50)) || '',
        w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10,
        cx: r.left + r.width / 2, cy: r.top + r.height / 2,
        inline: getComputedStyle(el).display.indexOf('inline') === 0,
        text: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 30),
      });
    }
  }

  // SC 2.5.8 punya dua pengecualian: target inline dalam blok teks, dan spacing
  // (lingkaran 24px tidak beririsan dengan lingkaran target lain).
  const targetViolations = smallTargets.filter(t => {
    if (t.inline && t.text) return false;
    for (const o of focusRects) {
      const dx = o.x - t.cx, dy = o.y - t.cy;
      if (Math.sqrt(dx * dx + dy * dy) < 24) return true;
    }
    return false;
  }).map(({ cx, cy, ...rest }) => rest);
  const inlineExempt = smallTargets.filter(t => t.inline && t.text).length;
  const spacingExempt = smallTargets.length - targetViolations.length - inlineExempt;

  const landmarks = {
    banner: document.querySelectorAll('[role="banner"], header:not([role])').length,
    main: document.querySelectorAll('[role="main"], main').length,
    nav: document.querySelectorAll('[role="navigation"], nav').length,
  };

  return {
    viewportWidth: vw,
    scrollWidth: scroller,
    horizontalScroll: scroller > vw + 2,
    offenders,
    focusableCount: focusables.length,
    positiveTabindexCount: positiveTabindex.length,
    firstFocusable: firstFocusable
      ? (firstFocusable.tagName.toLowerCase() + '.' + String(firstFocusable.className || '').slice(0, 50))
      : null,
    skipLink,
    smallTargets: targetViolations.slice(0, 8),
    smallTargetCount: targetViolations.length,
    smallTargetInlineExempt: inlineExempt,
    smallTargetSpacingExempt: Math.max(spacingExempt, 0),
    landmarks,
  };
};

async function main() {
  const [urlsFile, outputDir, concurrencyArg] = process.argv.slice(2);
  if (!urlsFile || !outputDir) {
    console.error('Usage: node layout_check.js <urls-file> <output-dir> [concurrency]');
    process.exit(1);
  }
  const concurrency = parseInt(concurrencyArg || '3', 10);
  const executablePath = findChrome();
  if (!executablePath) {
    console.error('Chrome tidak ditemukan');
    process.exit(1);
  }

  const urls = fs.readFileSync(urlsFile, 'utf-8')
    .split('\n').map(u => u.trim()).filter(u => u && !u.startsWith('#'));
  fs.mkdirSync(outputDir, { recursive: true });

  const queue = urls.map((url, i) => ({ url, i }));
  const total = queue.length;
  let done = 0, skipped = 0;
  const failed = [];
  const startedAt = Date.now();

  const browser = await puppeteer.launch({
    executablePath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  async function check(item) {
    const outFile = path.join(outputDir, `${slug(item.url, item.i)}.json`);
    if (fs.existsSync(outFile)) { skipped++; done++; return; }

    let page;
    try {
      page = await browser.newPage();
      await page.setUserAgent('WebQA-AccessibilityBot/1.0 (+audit aksesibilitas; hanya GET)');
      await page.setViewport({ width: 1280, height: 800 });
      await page.goto(item.url, { waitUntil: 'networkidle2', timeout: 45000 });
      await new Promise(r => setTimeout(r, 1200));

      const at1280 = await page.evaluate(MEASURE);
      await page.setViewport({ width: 320, height: 800 });
      await new Promise(r => setTimeout(r, 900));
      const at320 = await page.evaluate(MEASURE);
      await page.setViewport({ width: 640, height: 800 });
      await new Promise(r => setTimeout(r, 900));
      const at640 = await page.evaluate(MEASURE);

      fs.writeFileSync(outFile, JSON.stringify({
        url: item.url,
        checkedAt: new Date().toISOString(),
        desktop1280: at1280,
        narrow320: at320,
        zoom200_640: at640,
      }, null, 2));

      const flags = [];
      if (at320.horizontalScroll) flags.push('reflow320');
      if (at640.horizontalScroll) flags.push('zoom200');
      if (!at1280.skipLink) flags.push('no-skiplink');
      if (at1280.smallTargetCount) flags.push(`small${at1280.smallTargetCount}`);
      if (at1280.positiveTabindexCount) flags.push(`tabindex+${at1280.positiveTabindexCount}`);
      console.log(`[LAYOUT] ${done + 1}/${total} ${flags.length ? flags.join(',') : 'ok'}  ${item.url}`);
    } catch (err) {
      failed.push({ url: item.url, error: err.message });
      fs.writeFileSync(outFile.replace(/\.json$/, '.error.json'),
        JSON.stringify({ url: item.url, error: err.message }, null, 2));
      console.error(`[LAYOUT ERROR] ${item.url} -> ${err.message}`);
    } finally {
      if (page) await page.close().catch(() => {});
      done++;
    }

    if (done % 25 === 0 || done === total) {
      const mins = ((Date.now() - startedAt) / 60000).toFixed(1);
      const rate = done / ((Date.now() - startedAt) / 60000);
      console.log(`[LAYOUT] progress ${done}/${total} | ${mins} mnt | ETA ${rate > 0 ? ((total - done) / rate).toFixed(0) : '?'} mnt | skip ${skipped} | error ${failed.length}`);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, total) }, async () => {
    while (queue.length) await check(queue.shift());
  }));
  await browser.close();

  console.log(`[LAYOUT] DONE ${done}/${total} | skip ${skipped} | error ${failed.length} | ` +
    `${((Date.now() - startedAt) / 60000).toFixed(1)} mnt`);
}

main().catch(e => { console.error(e); process.exit(1); });