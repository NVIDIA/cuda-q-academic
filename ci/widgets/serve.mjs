import { createServer } from 'node:http';
import { readFile, realpath, stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ROOT, SITE_PREFIX, sitePath } from './site.mjs';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
};

export function createSiteServer(root = ROOT) {
  const resolvedRoot = resolve(root);
  return createServer(async (request, response) => {
    const send = (status, body = '') => {
      response.writeHead(status, {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-store',
      });
      response.end(request.method === 'HEAD' ? undefined : body);
    };
    try {
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        send(405, 'Method Not Allowed');
        return;
      }
      let pathname;
      try {
        pathname = new URL(request.url, 'http://127.0.0.1').pathname;
      } catch {
        send(400, 'Bad Request');
        return;
      }
      if (!pathname.startsWith(SITE_PREFIX)) {
        send(404, 'Not Found');
        return;
      }
      let relative;
      try {
        relative = sitePath(pathname);
      } catch {
        send(400, 'Bad Request');
        return;
      }
      if (!relative || relative.split('/').some(segment => segment.startsWith('.'))) {
        send(404, 'Not Found');
        return;
      }
      const filePath = resolve(resolvedRoot, relative);
      if (filePath !== resolvedRoot && !filePath.startsWith(resolvedRoot + sep)) {
        send(404, 'Not Found');
        return;
      }
      let stats;
      let realFile;
      try {
        stats = await stat(filePath);
        realFile = await realpath(filePath);
      } catch {
        send(404, 'Not Found');
        return;
      }
      const realRoot = await realpath(resolvedRoot).catch(() => resolvedRoot);
      if (!stats.isFile() || (realFile !== realRoot && !realFile.startsWith(realRoot + sep))) {
        send(404, 'Not Found');
        return;
      }
      let body;
      try {
        body = await readFile(realFile);
      } catch {
        send(404, 'Not Found');
        return;
      }
      response.writeHead(200, {
        'Content-Type': MIME_TYPES[extname(filePath).toLowerCase()] ?? 'application/octet-stream',
        'Content-Length': body.length,
        'Cache-Control': 'no-store',
        'X-Widget-Checkout': 'local',
      });
      response.end(request.method === 'HEAD' ? undefined : body);
    } catch {
      if (!response.headersSent) send(500, 'Internal Server Error');
      else response.destroy();
    }
  });
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const server = createSiteServer();
  server.listen(4173, '127.0.0.1', () => {
    console.log(`Serving ${ROOT} at http://127.0.0.1:4173${SITE_PREFIX}`);
  });
}
