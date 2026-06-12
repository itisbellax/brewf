// BREWF service worker — offline support + installable PWA.
// Bump CACHE when shipping changes so old caches get cleared on activate.
const CACHE = 'brewf-v1';
const SHELL = [
  './',
  './index.html',
  './brewF.png',
  './CabinetGrotesk-Black.ttf',
  './manifest.webmanifest'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Fresh content first: today's articles + podcast. Fall back to cache when offline.
  if (url.pathname.endsWith('articles.json') || url.pathname.endsWith('podcast.mp3')) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Everything else (app shell, fonts, CDN libs): cache-first, then network.
  e.respondWith(
    caches.match(req).then((cached) =>
      cached || fetch(req).then((res) => {
        const cacheable =
          res.ok &&
          (url.origin === location.origin ||
            req.url.startsWith('https://unpkg.com') ||
            req.url.startsWith('https://fonts.'));
        if (cacheable) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => cached)
    )
  );
});
