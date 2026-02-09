import { apiFetch } from './client';

export interface IntegrationStatus {
	provider: string;
	connected: boolean;
	provider_user_id: string | null;
	connected_at: string | null;
}

export interface SyncResult {
	imported_count: number;
	skipped_count: number;
}

export function getStravaAuthUrl(token: string) {
	return apiFetch<{ url: string }>('/api/integrations/strava/auth-url', { token });
}

export function connectStrava(token: string, code: string) {
	return apiFetch<{ connected: boolean }>(`/api/integrations/strava/callback?code=${encodeURIComponent(code)}`, {
		method: 'POST',
		token
	});
}

export function disconnectStrava(token: string) {
	return apiFetch<void>('/api/integrations/strava', {
		method: 'DELETE',
		token
	});
}

export function getIntegrationStatus(token: string) {
	return apiFetch<IntegrationStatus[]>('/api/integrations/status', { token });
}

export function syncStrava(token: string) {
	return apiFetch<SyncResult>('/api/integrations/strava/sync', {
		method: 'POST',
		token
	});
}
