// Very small service worker for offline caching of basic assets (optional)
const CACHE = 'fingest-v1';
const urls = [
  '/',
  '/static/style.css',
  '/static/default-avatar.svg',
];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(urls)));
});
self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
