import assert from 'node:assert/strict';
import { existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = fileURLToPath(new URL('../../', import.meta.url));
export const SITE_PREFIX = '/cuda-q-academic/';
export const PUBLIC_SITE = `https://nvidia.github.io${SITE_PREFIX}`;
export const LOCAL_SITE = `http://127.0.0.1:4173${SITE_PREFIX}`;

export function sitePath(reference, page = 'index.html') {
  const url = new URL(reference, new URL(page, PUBLIC_SITE));
  if (url.origin !== new URL(PUBLIC_SITE).origin || !url.pathname.startsWith(SITE_PREFIX)) return null;
  let path = decodeURIComponent(url.pathname.slice(SITE_PREFIX.length));
  assert(!path.startsWith('/') && !path.includes('\\') && !path.split('/').includes('..'), 'Unsafe site path');
  if (!path || path.endsWith('/')) path += 'index.html';
  return path;
}

export function htmlFiles(directory = ROOT, prefix = '') {
  const excluded = new Set(['node_modules', 'ci', 'tests', 'test-results', 'playwright-report']);
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    if (entry.name.startsWith('.') || excluded.has(entry.name)) return [];
    const relative = prefix + entry.name;
    if (entry.isDirectory()) return htmlFiles(join(directory, entry.name), relative + '/');
    return entry.isFile() && entry.name.endsWith('.html') ? [relative] : [];
  }).sort();
}

export function validateCatalog(catalog, exists = path => existsSync(join(ROOT, path))) {
  assert(Array.isArray(catalog.widget_gallery_order) && catalog.widget_gallery_order.length > 0, 'Missing widget gallery order');
  assert(catalog.widgets && typeof catalog.widgets === 'object', 'Missing widgets');
  assert.equal(new Set(catalog.widget_gallery_order).size, catalog.widget_gallery_order.length, 'Duplicate gallery IDs');
  for (const id of catalog.widget_gallery_order) assert(catalog.widgets[id], `Unknown widget ${id}`);
  return Object.entries(catalog.widgets).flatMap(([id, widget]) => {
    if (widget.coming_soon === true) return [];
    assert.equal(typeof widget.live_url, 'string', `Missing live URL for ${id}`);
    assert(widget.live_url.trim().length > 0, `Missing live URL for ${id}`);
    const path = sitePath(widget.live_url);
    assert(path && path.endsWith('.html'), `Invalid widget URL for ${id}`);
    if (widget.source_repo_path) assert.equal(widget.source_repo_path, path, `Source/live URL mismatch for ${id}`);
    assert(exists(path), `Missing widget page: ${path}`);
    return [path];
  });
}

export function essentialRequest(request) {
  const url = new URL(request.url());
  if (['fonts.googleapis.com', 'fonts.gstatic.com'].includes(url.hostname)) return false;
  return ['document', 'script', 'stylesheet', 'image', 'xhr', 'fetch'].includes(request.resourceType());
}
