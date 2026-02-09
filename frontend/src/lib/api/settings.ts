import { apiFetch } from './client';

interface UserResponse {
	id: string;
	email: string;
	display_name: string | null;
	preferences: Record<string, string>;
}

export function updateProfile(token: string, data: { display_name?: string; email?: string }) {
	return apiFetch<UserResponse>('/api/auth/me', {
		method: 'PATCH',
		token,
		body: JSON.stringify(data)
	});
}

export function changePassword(
	token: string,
	data: { current_password: string; new_password: string }
) {
	return apiFetch<void>('/api/auth/change-password', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function updatePreferences(
	token: string,
	data: { weight_unit?: string; distance_unit?: string; theme?: string }
) {
	return apiFetch<UserResponse>('/api/auth/preferences', {
		method: 'PATCH',
		token,
		body: JSON.stringify(data)
	});
}
