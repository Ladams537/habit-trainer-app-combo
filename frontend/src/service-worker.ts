/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;

const CACHE_NAME = `cache-${version}`;
const ASSETS = [...build, ...files];

// Install: precache app shell
sw.addEventListener('install', (event) => {
	event.waitUntil(
		caches
			.open(CACHE_NAME)
			.then((cache) => cache.addAll(ASSETS))
			.then(() => sw.skipWaiting())
	);
});

// Activate: clean old caches
sw.addEventListener('activate', (event) => {
	event.waitUntil(
		caches
			.keys()
			.then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
			.then(() => sw.clients.claim())
	);
});

// Fetch: network-first for API, cache-first for assets
sw.addEventListener('fetch', (event) => {
	const url = new URL(event.request.url);

	// Skip non-GET and cross-origin
	if (event.request.method !== 'GET') {
		// Queue failed mutations for offline replay
		if (['POST', 'PATCH', 'PUT', 'DELETE'].includes(event.request.method) && url.pathname.startsWith('/api/')) {
			event.respondWith(
				fetch(event.request.clone()).catch(async () => {
					// Store in offline queue
					const body = await event.request.clone().text();
					const client = await sw.clients.get(event.clientId ?? '');
					if (client) {
						client.postMessage({
							type: 'QUEUE_REQUEST',
							url: event.request.url,
							method: event.request.method,
							body,
							headers: Object.fromEntries(event.request.headers.entries())
						});
					}
					return new Response(JSON.stringify({ queued: true }), {
						status: 202,
						headers: { 'Content-Type': 'application/json' }
					});
				})
			);
			return;
		}
		return;
	}

	if (url.origin !== sw.location.origin) return;

	// Static assets: cache-first
	if (ASSETS.includes(url.pathname)) {
		event.respondWith(
			caches.match(event.request).then((cached) => cached || fetch(event.request))
		);
		return;
	}

	// API requests: network-first with cache fallback
	if (url.pathname.startsWith('/api/')) {
		event.respondWith(
			fetch(event.request)
				.then((response) => {
					const clone = response.clone();
					caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
					return response;
				})
				.catch(() => caches.match(event.request).then((cached) => cached || offlineResponse()))
		);
		return;
	}

	// Navigation requests: network-first, offline fallback
	if (event.request.mode === 'navigate') {
		event.respondWith(
			fetch(event.request).catch(() =>
				caches.match(event.request).then((cached) => cached || caches.match('/offline'))
			)
		);
		return;
	}

	// Everything else: network-first
	event.respondWith(
		fetch(event.request)
			.then((response) => {
				const clone = response.clone();
				caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
				return response;
			})
			.catch(() => caches.match(event.request).then((cached) => cached || offlineResponse()))
	);
});

function offlineResponse() {
	return new Response('Offline', { status: 503, statusText: 'Offline' });
}
