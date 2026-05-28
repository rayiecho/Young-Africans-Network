const CACHE_NAME = 'yan-cache-v7';
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

// ── PUSH NOTIFICATIONS ─────────────────────────────────
self.addEventListener('push', function(event) {
  let data = { title: 'YAN Notification', body: 'You have a new update', icon: '/images/logo.jpeg' };
  if (event.data) {
    try { data = event.data.json(); } catch(e) { data.body = event.data.text(); }
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '/images/logo.jpeg',
      badge: '/images/logo.jpeg',
      vibrate: [200, 100, 200],
      data: { url: data.url || 'https://youngafricansnetwork.org/community.html' },
      actions: [
        { action: 'open', title: 'Open YAN' },
        { action: 'close', title: 'Dismiss' }
      ]
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  if (event.action === 'close') return;
  const url = event.notification.data?.url || 'https://youngafricansnetwork.org/community.html';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
