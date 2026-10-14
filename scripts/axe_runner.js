/**
 * axe_runner.js - Scan axe-core batch dengan SATU instance browser + concurrency.
 *
 * Dipanggil oleh scripts/run_axe.py:
 *   node scripts/axe_runner.js <urls-file> <output-dir> [concurrency] [chrome-path]
 *
 * - resume: JSON yang sudah ada di output-dir dilewati
 * - output: <output-dir>/<index>-<slug>.json per URL + summary.json
 */

const fs = require('fs');
const path = require('path');
const { AxePuppeteer } = require('@axe-core/puppeteer');
const puppeteer = require('puppeteer-core');

const CHROME_CANDIDATES = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
];

function findChrome() {
  const fromEnv = process.env.CHROME_PATH;
  if (fromEnv && fs.existsSync(fromEnv)) return fromEnv;
  for (const p of CHROME_CANDIDATES) {
    if (fs.existsSync(p)) return p;
  }
  return undefined;
}

function slug(url, index) {
  const safe = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]+/g, '_').slice(0, 80);
  return `${String(index).padStart(4, '0')}_${safe}`;
}

async function main() {
  const [urlsFile, outputDir, concurrencyArg, chromePath] = process.argv.slice(2);
  if (!urlsFile || !outputDir) {
    console.error('Usage: node axe_runner.js <urls-file> <output-dir> [concurrency] [chrome-path]');
    process.exit(1);
  }

  const concurrency = parseInt(concurrencyArg || '3', 10);
  const executablePath = chromePath || findChrome();
  if (!executablePath) {
    console.error('Chrome tidak ditemukan. Set CHROME_PATH atau pass path sebagai argumen 4.');
    process.exit(1);
  }

  const urls = fs.readFileSync(urlsFile, 'utf-8')
    .split('\n').map(u => u.trim()).filter(u => u && !u.startsWith('#'));

  fs.mkdirSync(outputDir, { recursive: true });

  const queue = urls.map((url, i) => ({ url, i }));
  const total = queue.length;
  let done = 0;
  let skipped = 0;
  const failed = [];
  const startedAt = Date.now();

  console.log(`[AXE] ${total} URL | concurrency ${concurrency}`);
  console.log(`[AXE] chrome: ${executablePath}`);
  console.log(`[AXE] output: ${outputDir}`);

  const browser = await puppeteer.launch({
    executablePath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
           '--disable-gpu', '--window-size=1280,720'],
  });

  async function scan(item) {
    const outFile = path.join(outputDir, `${slug(item.url, item.i)}.json`);
    if (fs.existsSync(outFile)) {
      skipped++;
      done++;
      return;
    }

    let page;
    try {
      page = await browser.newPage();
      await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });
      await page.setUserAgent('WebQA-AccessibilityBot/1.0 (+audit aksesibilitas; hanya GET)');
      await page.goto(item.url, { waitUntil: 'networkidle2', timeout: 45000 });
      await new Promise(r => setTimeout(r, 1500));

      const results = await new AxePuppeteer(page).analyze();
      fs.writeFileSync(outFile, JSON.stringify({
        url: item.url,
        scannedAt: new Date().toISOString(),
        engine: results.testEngine,
        violations: results.violations,
        passes: results.passes.map(p => p.id),
        incomplete: results.incomplete,
        inapplicable: results.inapplicable,
      }, null, 2));
      console.log(`[AXE] ${done + 1}/${total} ${results.violations.length} violation  ${item.url}`);
    } catch (err) {
      failed.push({ url: item.url, error: err.message });
      fs.writeFileSync(outFile.replace(/\.json$/, '.error.json'),
        JSON.stringify({ url: item.url, error: err.message }, null, 2));
      console.error(`[AXE ERROR] ${done + 1}/${total} ${item.url} -> ${err.message}`);
    } finally {
      if (page) await page.close().catch(() => {});
      done++;
    }

    if (done % 25 === 0 || done === total) {
      const mins = ((Date.now() - startedAt) / 60000).toFixed(1);
      const rate = done / ((Date.now() - startedAt) / 60000);
      const eta = rate > 0 ? ((total - done) / rate).toFixed(0) : '?';
      console.log(`[AXE] progress ${done}/${total} | ${mins} mnt | ETA ${eta} mnt | skip ${skipped} | error ${failed.length}`);
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, total) }, async () => {
    while (queue.length) {
      await scan(queue.shift());
    }
  });

  await Promise.all(workers);
  await browser.close();

  const files = fs.readdirSync(outputDir).filter(f => f.endsWith('.json') && !f.endsWith('.error.json'));
  const byRule = {};
  const byImpact = { critical: 0, serious: 0, moderate: 0, minor: 0 };
  let totalViolations = 0;

  for (const f of files) {
    const data = JSON.parse(fs.readFileSync(path.join(outputDir, f), 'utf-8'));
    for (const v of data.violations || []) {
      totalViolations++;
      byRule[v.id] = (byRule[v.id] || 0) + 1;
      if (v.impact && byImpact[v.impact] !== undefined) byImpact[v.impact]++;
    }
  }

  const summary = {
    tool: 'axe-core',
    runAt: new Date().toISOString(),
    totalUrls: total,
    scanned: files.length,
    skippedFromPreviousRun: skipped,
    failed: failed.length,
    failedList: failed,
    elapsedMin: +((Date.now() - startedAt) / 60000).toFixed(1),
    totalViolations,
    violationsByImpact: byImpact,
    violationsByRule: Object.entries(byRule).sort((a, b) => b[1] - a[1]),
  };
  fs.writeFileSync(path.join(outputDir, 'summary.json'), JSON.stringify(summary, null, 2));

  console.log('[AXE] DONE');
  console.log(`[AXE] scanned ${files.length}/${total}, error ${failed.length}, ${summary.elapsedMin} mnt`);
  console.log(`[AXE] total violations ${totalViolations}`, JSON.stringify(byImpact));
  for (const [rule, count] of summary.violationsByRule.slice(0, 12)) {
    console.log(`   ${rule}: ${count}`);
  }
}

main().catch(err => {
  console.error('[AXE] fatal:', err);
  process.exit(1);
});