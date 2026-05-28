const CACHE_NAME = 'yan-cache-v5';
const STATIC_ASSETS = [
  '/images/logo.jpeg'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) { return key !== CACHE_NAME; })
          .map(function(key) { return caches.delete(key); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  const url = event.request.url;
  
  // Never cache HTML files or external APIs
  if (url.endsWith('.html') || url.endsWith('/') ||
      url.includes('firestore.googleapis.com') ||
      url.includes('gstatic.com') ||
      url.includes('googleapis.com') ||
      url.includes('firebase') ||
      url.includes('cloudinary') ||
      url.includes('emailjs') ||
      url.includes('daily.co') ||
      url.includes('anthropic') ||
      url.includes('workers.dev')) return;

  // Cache only static assets like images
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      return cached || fetch(event.request).then(function(response) {
        if (response && response.status === 200 && url.includes('/images/')) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      });
    })
  );
});
