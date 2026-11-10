import assert from 'node:assert/strict';
import { once } from 'node:events';
import { describe, test } from 'node:test';
import { createSiteServer } from '../ci/widgets/serve.mjs';
import { PUBLIC_SITE, SITE_PREFIX, essentialRequest, sitePath, validateCatalog } from '../ci/widgets/site.mjs';
import { waitForDeployment } from '../ci/widgets/wait-for-deployment.mjs';

const REPO = '/repos/NVIDIA/cuda-q-academic';
const SHA = 'a'.repeat(40);
const OTHER_SHA = 'b'.repeat(40);

describe('sitePath', () => {
  test('resolves nested relative paths', () => {
    assert.equal(sitePath('interactive_widgets/binary_fraction.html'), 'interactive_widgets/binary_fraction.html');
    assert.equal(sitePath('../random_walk.html', 'quick-start-to-quantum/interactive_widget/cnot-visualization.html'), 'quick-start-to-quantum/random_walk.html');
  });

  test('resolves absolute production URLs and ignores query/fragment', () => {
    assert.equal(sitePath(`${PUBLIC_SITE}index.html?track=t1#grid`), 'index.html');
  });

  test('maps root and trailing slashes to index.html', () => {
    assert.equal(sitePath(PUBLIC_SITE), 'index.html');
    assert.equal(sitePath(`${PUBLIC_SITE}interactive_widgets/`), 'interactive_widgets/index.html');
  });

  test('rejects external hosts and other GitHub Pages projects', () => {
    assert.equal(sitePath('https://github.com/NVIDIA/cuda-q-academic/blob/widgets-as-html/index.html'), null);
    assert.equal(sitePath('https://nvidia.github.io/other-project/index.html'), null);
    assert.equal(sitePath('https://raw.githubusercontent.com/NVIDIA/cuda-q-academic/main/curriculum.json'), null);
  });

  test('rejects non-HTTP schemes', () => {
    assert.equal(sitePath('data:text/html;base64,AAAA'), null);
    assert.equal(sitePath('mailto:someone@example.com'), null);
    assert.equal(sitePath('javascript:void(0)'), null);
  });

  test('rejects encoded traversal and backslashes', () => {
    assert.equal(sitePath(`${PUBLIC_SITE}%2e%2e/escape.html`), null);
    assert.throws(() => sitePath(`${PUBLIC_SITE}widgets/%2e%2e%2f%2e%2e%2fescape.html`), /Unsafe site path/);
    assert.throws(() => sitePath(`${PUBLIC_SITE}dir%5cfile.html`), /Unsafe site path/);
  });

  test('rejects malformed escapes in local references', () => {
    assert.throws(() => sitePath('interactive_widgets/%broken.html'), URIError);
  });
});

describe('validateCatalog', () => {
  const base = () => ({
    widget_gallery_order: ['w1'],
    widgets: {
      w1: {
        live_url: `${PUBLIC_SITE}interactive_widgets/w1.html`,
        source_repo_path: 'interactive_widgets/w1.html',
      },
    },
  });

  test('accepts a valid catalog and returns live page paths', () => {
    assert.deepEqual(validateCatalog(base(), () => true), ['interactive_widgets/w1.html']);
  });

  test('falls back to live_url when source_repo_path is null', () => {
    const catalog = base();
    catalog.widgets.w1.source_repo_path = null;
    assert.deepEqual(validateCatalog(catalog, () => true), ['interactive_widgets/w1.html']);
  });

  test('allows coming_soon entries without URLs', () => {
    const catalog = base();
    catalog.widget_gallery_order.push('w2');
    catalog.widgets.w2 = { coming_soon: true, live_url: null, source_repo_path: null };
    assert.deepEqual(validateCatalog(catalog, () => true), ['interactive_widgets/w1.html']);
  });

  test('rejects malformed JSON at parse time', () => {
    assert.throws(() => JSON.parse('{ not json '), SyntaxError);
  });

  test('rejects unknown gallery IDs', () => {
    const catalog = base();
    catalog.widget_gallery_order.push('ghost');
    assert.throws(() => validateCatalog(catalog, () => true), /Unknown widget ghost/);
  });

  test('rejects duplicate gallery IDs', () => {
    const catalog = base();
    catalog.widget_gallery_order = ['w1', 'w1'];
    assert.throws(() => validateCatalog(catalog, () => true), /Duplicate gallery IDs/);
  });

  test('rejects empty live URLs instead of treating them as the homepage', () => {
    for (const value of ['', '   ']) {
      const catalog = base();
      catalog.widgets.w1.live_url = value;
      catalog.widgets.w1.source_repo_path = null;
      assert.throws(() => validateCatalog(catalog, () => true), /Missing live URL for w1/);
    }
  });

  test('rejects widgets whose page is missing', () => {
    assert.throws(() => validateCatalog(base(), () => false), /Missing widget page/);
  });

  test('rejects widgets without a live URL', () => {
    const catalog = base();
    delete catalog.widgets.w1.live_url;
    assert.throws(() => validateCatalog(catalog, () => true), /Missing live URL for w1/);
  });

  test('rejects source paths that disagree with the live URL', () => {
    const catalog = base();
    catalog.widgets.w1.source_repo_path = 'interactive_widgets/other.html';
    assert.throws(() => validateCatalog(catalog, () => true), /Source\/live URL mismatch for w1/);
  });
});

describe('essentialRequest', () => {
  const fake = (url, resourceType) => ({ url: () => url, resourceType: () => resourceType });

  test('treats documents, scripts, styles, images, xhr and fetch as essential', () => {
    for (const type of ['document', 'script', 'stylesheet', 'image', 'xhr', 'fetch']) {
      assert.equal(essentialRequest(fake('https://cdn.example.com/app.js', type)), true, type);
    }
  });

  test('ignores font resources', () => {
    assert.equal(essentialRequest(fake('https://cdn.example.com/font.woff2', 'font')), false);
    assert.equal(essentialRequest(fake('https://example.com/x', 'media')), false);
    assert.equal(essentialRequest(fake('wss://example.com/socket', 'websocket')), false);
  });

  test('ignores Google Fonts even for essential resource types', () => {
    assert.equal(essentialRequest(fake('https://fonts.googleapis.com/css2?family=Inter', 'stylesheet')), false);
    assert.equal(essentialRequest(fake('https://fonts.gstatic.com/s/inter/font.woff2', 'font')), false);
  });
});

describe('createSiteServer', () => {
  async function serve(t) {
    const server = createSiteServer();
    t.after(() => new Promise(resolve => server.close(resolve)));
    server.listen(0, '127.0.0.1');
    await once(server, 'listening');
    return `http://127.0.0.1:${server.address().port}`;
  }

  test('serves the site index under the prefix with the checkout marker', async t => {
    const base = await serve(t);
    const response = await fetch(`${base}${SITE_PREFIX}index.html`);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('x-widget-checkout'), 'local');
    assert.equal(response.headers.get('cache-control'), 'no-store');
    assert.match(await response.text(), /cuda-q/i);
  });

  test('answers HEAD without a body', async t => {
    const base = await serve(t);
    const response = await fetch(`${base}${SITE_PREFIX}index.html`, { method: 'HEAD' });
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('x-widget-checkout'), 'local');
    assert.equal(await response.text(), '');
  });

  test('returns 404 for unknown, out-of-prefix and hidden paths', async t => {
    const base = await serve(t);
    for (const path of [
      `${SITE_PREFIX}no-such-file.html`,
      `${SITE_PREFIX}interactive_widgets`,
      '/other-project/index.html',
      '/index.html',
      `${SITE_PREFIX}.git/config`,
      `${SITE_PREFIX}.env`,
      `${SITE_PREFIX}interactive_widgets/.hidden.html`,
    ]) {
      const response = await fetch(`${base}${path}`);
      assert.equal(response.status, 404, path);
    }
  });

  test('rejects encoded traversal with 400 or 404', async t => {
    const base = await serve(t);
    const response = await fetch(`${base}${SITE_PREFIX}widgets/%2e%2e%2f%2e%2e%2fsecret.txt`);
    assert.ok([400, 404].includes(response.status), `status ${response.status}`);
  });

  test('rejects non-GET/HEAD methods', async t => {
    const base = await serve(t);
    const response = await fetch(`${base}${SITE_PREFIX}index.html`, { method: 'POST' });
    assert.equal(response.status, 405);
  });
});

describe('waitForDeployment', () => {
  const deploymentsPath = `${REPO}/deployments?environment=github-pages&per_page=1`;
  const statusPath = id => `${REPO}/deployments/${id}/statuses?per_page=1`;
  const branchPath = `${REPO}/branches/widgets-as-html`;

  function clock() {
    let time = 0;
    return { now: () => time, pause: async ms => { time += ms; } };
  }

  function responder(table) {
    const calls = [];
    const request = async path => {
      calls.push(path);
      const entry = table[path];
      if (entry === undefined) throw new Error(`Unexpected API request: ${path}`);
      return typeof entry === 'function' ? entry() : entry;
    };
    return { request, calls };
  }

  function queue(...values) {
    let index = 0;
    return () => values[Math.min(index++, values.length - 1)];
  }

  test('returns the deployment once the latest deployment of the commit succeeds', async () => {
    const { request, calls } = responder({
      [deploymentsPath]: [{ id: 7, sha: SHA }],
      [statusPath(7)]: [{ state: 'success' }],
      [branchPath]: { commit: { sha: SHA } },
    });
    const { now, pause } = clock();
    const deployment = await waitForDeployment({ sha: SHA, request, now, pause });
    assert.equal(deployment.id, 7);
    assert.deepEqual(calls, [deploymentsPath, statusPath(7), branchPath]);
  });

  test('keeps polling when the latest deployment is for a different commit', async () => {
    const { request, calls } = responder({
      [deploymentsPath]: queue([{ id: 1, sha: OTHER_SHA }], [{ id: 2, sha: SHA }]),
      [statusPath(2)]: [{ state: 'success' }],
      [branchPath]: { commit: { sha: SHA } },
    });
    const { now, pause } = clock();
    const deployment = await waitForDeployment({ sha: SHA, request, now, pause });
    assert.equal(deployment.id, 2);
    assert.deepEqual(calls, [deploymentsPath, deploymentsPath, statusPath(2), branchPath]);
  });

  test('waits through in-progress states', async () => {
    const { request, calls } = responder({
      [deploymentsPath]: [{ id: 3, sha: SHA }],
      [statusPath(3)]: queue([{ state: 'queued' }], [{ state: 'pending' }], [{ state: 'success' }]),
      [branchPath]: { commit: { sha: SHA } },
    });
    const { now, pause } = clock();
    const deployment = await waitForDeployment({ sha: SHA, request, now, pause });
    assert.equal(deployment.id, 3);
    assert.equal(calls.filter(path => path === statusPath(3)).length, 3);
  });

  test('does not accept a matching deployment behind a newer non-matching one', async () => {
    const { request } = responder({
      [deploymentsPath]: [{ id: 9, sha: OTHER_SHA }, { id: 8, sha: SHA }],
    });
    const { now, pause } = clock();
    await assert.rejects(
      waitForDeployment({ sha: SHA, request, timeoutMs: 5, now, pause }),
      /Timed out waiting/
    );
  });

  for (const state of ['failure', 'error', 'inactive']) {
    test(`throws when the latest deployment is ${state}`, async () => {
      const { request } = responder({
        [deploymentsPath]: [{ id: 4, sha: SHA }],
        [statusPath(4)]: [{ state }],
      });
      const { now, pause } = clock();
      await assert.rejects(
        waitForDeployment({ sha: SHA, request, now, pause }),
        new RegExp(`deployment 4 is ${state}`)
      );
    });
  }

  test('throws when the branch has moved past the tested commit', async () => {
    const { request } = responder({
      [deploymentsPath]: [{ id: 5, sha: SHA }],
      [statusPath(5)]: [{ state: 'success' }],
      [branchPath]: { commit: { sha: OTHER_SHA } },
    });
    const { now, pause } = clock();
    await assert.rejects(
      waitForDeployment({ sha: SHA, request, now, pause }),
      /superseded/
    );
  });

  test('times out with no deployments and with no statuses', async () => {
    const empty = responder({ [deploymentsPath]: [] });
    const noStatus = responder({
      [deploymentsPath]: [{ id: 6, sha: SHA }],
      [statusPath(6)]: [],
    });
    for (const { request } of [empty, noStatus]) {
      const { now, pause } = clock();
      await assert.rejects(
        waitForDeployment({ sha: SHA, request, timeoutMs: 5, now, pause }),
        /Timed out waiting/
      );
    }
  });

  test('rejects missing or malformed SHAs', async () => {
    await assert.rejects(waitForDeployment({ sha: '' }), /CI_COMMIT_SHA/);
    await assert.rejects(waitForDeployment({ sha: 'abc123' }), /CI_COMMIT_SHA/);
    await assert.rejects(waitForDeployment({ sha: 'z'.repeat(40) }), /CI_COMMIT_SHA/);
  });

  test('rejects malformed API responses', async () => {
    const badDeployments = responder({ [deploymentsPath]: { not: 'an array' } });
    const { now, pause } = clock();
    await assert.rejects(
      waitForDeployment({ sha: SHA, request: badDeployments.request, now, pause }),
      /Unexpected GitHub deployments response/
    );
    const badStatuses = responder({
      [deploymentsPath]: [{ id: 10, sha: SHA }],
      [statusPath(10)]: 'oops',
    });
    await assert.rejects(
      waitForDeployment({ sha: SHA, request: badStatuses.request, now, pause }),
      /Unexpected GitHub deployment statuses response/
    );
  });
});
