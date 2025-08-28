// Service Worker for Swaccha Andhra Dashboard PWA
// Provides offline functionality and caching

const CACHE_NAME = 'swaccha-andhra-v1.0.0';
const STATIC_CACHE_NAME = 'swaccha-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'swaccha-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/assets/manifest.json',
  '/assets/style.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
  // Add more static assets as needed
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\//,
  /\/data\//,
  /_dash-/
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (request.destination === 'document') {
    // HTML pages - Network first, then cache
    event.respondWith(networkFirstStrategy(request));
  } else if (isStaticAsset(request)) {
    // Static assets - Cache first, then network
    event.respondWith(cacheFirstStrategy(request));
  } else if (isAPIRequest(request)) {
    // API requests - Network first with short cache
    event.respondWith(networkFirstWithShortCache(request));
  } else {
    // Other requests - Network first
    event.respondWith(networkFirstStrategy(request));
  }
});

// Network first strategy (for HTML and dynamic content)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', error);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page if available
    if (request.destination === 'document') {
      return caches.match('/offline.html') || createOfflineResponse();
    }
    
    return createOfflineResponse();
  }
}

// Cache first strategy (for static assets)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Update cache in background
    updateCacheInBackground(request);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Failed to fetch static asset', error);
    return createOfflineResponse();
  }
}

// Network first with short cache (for API requests)
async function networkFirstWithShortCache(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      
      // Add timestamp for cache invalidation
      const responseToCache = networkResponse.clone();
      responseToCache.headers.set('sw-cache-timestamp', Date.now().toString());
      
      cache.put(request, responseToCache);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: API request failed, trying cache', error);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse && !isCacheExpired(cachedResponse)) {
      return cachedResponse;
    }
    
    return createOfflineResponse();
  }
}

// Update cache in background
function updateCacheInBackground(request) {
  fetch(request)
    .then((response) => {
      if (response.ok) {
        caches.open(STATIC_CACHE_NAME)
          .then((cache) => cache.put(request, response));
      }
    })
    .catch(() => {
      // Silently fail background updates
    });
}

// Check if cache is expired (5 minutes for API responses)
function isCacheExpired(response) {
  const cacheTimestamp = response.headers.get('sw-cache-timestamp');
  if (!cacheTimestamp) return true;
  
  const cacheAge = Date.now() - parseInt(cacheTimestamp);
  const maxAge = 5 * 60 * 1000; // 5 minutes
  
  return cacheAge > maxAge;
}

// Check if request is for static assets
function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'image' ||
    request.destination === 'font' ||
    url.pathname.includes('/assets/') ||
    url.pathname.includes('/_dash-component-suites/') ||
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com'
  );
}

// Check if request is for API
function isAPIRequest(request) {
  return API_CACHE_PATTERNS.some(pattern => pattern.test(request.url));
}

// Create offline response
function createOfflineResponse() {
  return new Response(
    JSON.stringify({
      error: 'Offline',
      message: 'You are currently offline. Please check your internet connection.',
      timestamp: new Date().toISOString()
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
      }
    }
  );
}

// Handle background sync (if supported)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Background sync function
async function doBackgroundSync() {
  try {
    // Perform any background sync operations
    console.log('Service Worker: Background sync completed');
  } catch (error) {
    console.error('Service Worker: Background sync failed', error);
  }
}

// Handle push notifications (if needed)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || 'New update available',
      icon: '/assets/icon-192.png',
      badge: '/assets/icon-72.png',
      tag: 'swaccha-notification',
      vibrate: [100, 50, 100],
      data: data.data || {},
      actions: [
        {
          action: 'view',
          title: 'View Dashboard',
          icon: '/assets/icon-72.png'
        },
        {
          action: 'dismiss',
          title: 'Dismiss',
          icon: '/assets/icon-72.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Swaccha Andhra', options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'data-sync') {
    event.waitUntil(syncDataInBackground());
  }
});

async function syncDataInBackground() {
  try {
    // Sync data when app is in background
    console.log('Service Worker: Periodic sync completed');
  } catch (error) {
    console.error('Service Worker: Periodic sync failed', error);
  }
}