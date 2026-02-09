const DB_NAME = 'trainer-offline';
const STORE_NAME = 'queue';
const DB_VERSION = 1;

interface QueuedRequest {
	id?: number;
	url: string;
	method: string;
	body: string;
	headers: Record<string, string>;
	timestamp: number;
}

function openDB(): Promise<IDBDatabase> {
	return new Promise((resolve, reject) => {
		const request = indexedDB.open(DB_NAME, DB_VERSION);
		request.onupgradeneeded = () => {
			const db = request.result;
			if (!db.objectStoreNames.contains(STORE_NAME)) {
				db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
			}
		};
		request.onsuccess = () => resolve(request.result);
		request.onerror = () => reject(request.error);
	});
}

export async function queueRequest(
	url: string,
	method: string,
	body: string,
	headers: Record<string, string> = {}
): Promise<void> {
	const db = await openDB();
	const tx = db.transaction(STORE_NAME, 'readwrite');
	const store = tx.objectStore(STORE_NAME);
	store.add({ url, method, body, headers, timestamp: Date.now() } satisfies Omit<QueuedRequest, 'id'>);
	await new Promise<void>((resolve, reject) => {
		tx.oncomplete = () => resolve();
		tx.onerror = () => reject(tx.error);
	});
}

export async function replayQueue(): Promise<number> {
	const db = await openDB();
	const tx = db.transaction(STORE_NAME, 'readonly');
	const store = tx.objectStore(STORE_NAME);

	const items: QueuedRequest[] = await new Promise((resolve, reject) => {
		const request = store.getAll();
		request.onsuccess = () => resolve(request.result);
		request.onerror = () => reject(request.error);
	});

	let replayed = 0;
	for (const item of items) {
		try {
			await fetch(item.url, {
				method: item.method,
				body: item.body || undefined,
				headers: item.headers
			});
			// Remove from queue on success
			const deleteTx = db.transaction(STORE_NAME, 'readwrite');
			deleteTx.objectStore(STORE_NAME).delete(item.id!);
			await new Promise<void>((resolve) => {
				deleteTx.oncomplete = () => resolve();
			});
			replayed++;
		} catch {
			// Still offline, stop trying
			break;
		}
	}
	return replayed;
}

export async function getQueueSize(): Promise<number> {
	const db = await openDB();
	const tx = db.transaction(STORE_NAME, 'readonly');
	const store = tx.objectStore(STORE_NAME);
	return new Promise((resolve, reject) => {
		const request = store.count();
		request.onsuccess = () => resolve(request.result);
		request.onerror = () => reject(request.error);
	});
}
