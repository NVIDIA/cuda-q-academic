import { test as base, expect } from '@playwright/test';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  ROOT,
  PUBLIC_SITE,
  essentialRequest,
  htmlFiles,
  sitePath,
  validateCatalog,
} from '../ci/widgets/site.mjs';

const live = process.env.WIDGETS_LIVE === '1';
const LIVE_PAGES = [
  'visualization-gallery.html',
  'quick-start-to-quantum/interactive_widget/cnot-visualization.html',
  'interactive_widgets/binary_fraction.html',
];
const GALLERY_PATH = 'visualization-gallery.html';
const CNOT_PATH = 'quick-start-to-quantum/interactive_widget/cnot-visualization.html';
const BINARY_FRACTION_PATH = 'interactive_widgets/binary_fraction.html';

const test = base.extend({
  page: async ({ page, context }, use) => {
    const failures = [];
    page.on('pageerror', error => failures.push(error.message));
    page.on('requestfailed', request => {
      if (essentialRequest(request)) failures.push(`${request.url()}: ${request.failure()?.errorText}`);
    });
    page.on('response', response => {
      if (response.status() >= 400 && essentialRequest(response.request())) failures.push(`${response.status()} ${response.url()}`);
    });
    if (!live) await context.route(`${PUBLIC_SITE}**`, async route => {
      const url = new URL(route.request().url());
      const response = await route.fetch({ url: `http://127.0.0.1:4173${url.pathname}${url.search}`, maxRedirects: 0 });
      await route.fulfill({ response });
    });
    await use(page);
    expect(failures, 'Browser errors or failed essential resources').toEqual([]);
  },
});

async function openPage(page, path) {
  const response = await page.goto(path, { waitUntil: 'load' });
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(/\S/);
  if (path.endsWith('cudaq-hello-world.html')) {
    await expect(page.locator('.widget-container .controls strong').first()).toBeVisible();
  } else {
    await expect(page.locator('h1').first()).toBeVisible();
  }
  if (path === 'learningpath.html') {
    await expect.poll(() => page.locator('#grid-container .pathway-card').count()).toBeGreaterThan(0);
  }
  if (path === GALLERY_PATH) {
    await expect.poll(() => page.locator('.pathway-card:not(.coming-soon) .btn-nvidia-primary').count()).toBeGreaterThan(0);
  }
  await page.evaluate(() => window.MathJax?.startup?.promise);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  return response;
}

const pages = live ? LIVE_PAGES : htmlFiles();

test.describe('widget pages', () => {
  for (const path of pages) {
    test(`loads ${path}`, async ({ page }) => {
      await openPage(page, path);
      if (live) return;
      const references = await page.locator('[href], [src]').evaluateAll(elements =>
        elements.flatMap(element => ['href', 'src'].map(name => element.getAttribute(name)))
      );
      const missing = [];
      for (const reference of references) {
        if (!reference) continue;
        const target = sitePath(reference, path);
        if (target && !existsSync(join(ROOT, target))) missing.push(`${reference} -> ${target}`);
      }
      expect(missing, `Missing local resources referenced by ${path}`).toEqual([]);
    });
  }

  if (!live) {
    test('curriculum widget catalog resolves to committed pages', () => {
      const catalog = JSON.parse(readFileSync(join(ROOT, 'curriculum.json'), 'utf8'));
      const paths = validateCatalog(catalog);
      expect(paths.length).toBeGreaterThan(0);
    });

    test('production URLs are served from the local checkout', async ({ page }) => {
      const response = await page.goto(`${PUBLIC_SITE}index.html`);
      expect(response.headers()['x-widget-checkout']).toBe('local');
      await expect(page.locator('h1').first()).toBeVisible();
    });
  }

  test('CNOT visualizer computes the |11> state', async ({ page }) => {
    await openPage(page, CNOT_PATH);
    await page.selectOption('#q0-select', '1');
    await page.selectOption('#q1-select', '0');
    await expect(page.locator('#state-text')).toContainText('|11⟩');
    await expect(page.locator('#bar-11 .bar-value')).toHaveText('100.0%');
    for (const id of ['bar-00', 'bar-01', 'bar-10']) {
      await expect(page.locator(`#${id} .bar-value`)).toHaveText('0%');
    }
  });

  test('binary fraction explorer toggles bits', async ({ page }) => {
    await openPage(page, BINARY_FRACTION_PATH);
    const sum = page.locator('[aria-labelledby="current-label"]');
    await expect(sum).toHaveText('0.00000');
    const bit = page.getByRole('button', { name: /^Toggle bit 2⁻1\./ });
    await bit.click();
    await expect(sum).toHaveText('0.50000');
    await expect(bit).toHaveAttribute('aria-pressed', 'true');
    await bit.click();
    await expect(sum).toHaveText('0.00000');
  });

  test('gallery preview embeds the widget page', async ({ page }) => {
    await openPage(page, GALLERY_PATH);
    const card = page.locator('article.pathway-card').filter({ has: page.getByRole('heading', { name: 'CNOT Gate Visualizer' }) });
    const preview = card.getByRole('button', { name: 'Preview' });
    const frameResponse = live ? null : page.waitForResponse(response => response.url() === `${PUBLIC_SITE}${CNOT_PATH}`);
    await preview.click();
    await expect(page.locator('#preview-modal')).toHaveClass(/open/);
    await expect(page.locator('#modal-title')).toHaveText('CNOT Gate Visualizer');
    await expect(page.frameLocator('#preview-frame').locator('#q0-select')).toBeVisible();
    await expect(page.locator('#preview-frame')).toHaveAttribute('src', `${PUBLIC_SITE}${CNOT_PATH}`);
    if (frameResponse) expect((await frameResponse).headers()['x-widget-checkout']).toBe('local');
    await page.keyboard.press('Escape');
    await expect(page.locator('#preview-modal')).not.toHaveClass(/open/);
    await expect(page.locator('#preview-frame')).toHaveAttribute('src', '');
  });
});
