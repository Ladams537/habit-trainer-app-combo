import { fail, redirect } from '@sveltejs/kit';
import { apiFetch } from '$lib/api/client';
import { updateProfile, changePassword, updatePreferences } from '$lib/api/settings';
import { getIntegrationStatus, disconnectStrava, syncStrava } from '$lib/api/integrations';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) redirect(302, '/login');

	let strava = { connected: false, provider_user_id: null as string | null };

	if (locals.token) {
		try {
			const statuses = await getIntegrationStatus(locals.token);
			const stravaStatus = statuses.find((s) => s.provider === 'strava');
			if (stravaStatus) {
				strava = {
					connected: stravaStatus.connected,
					provider_user_id: stravaStatus.provider_user_id
				};
			}
		} catch {
			// Integrations endpoint may not be available yet
		}
	}

	return {
		user: locals.user,
		strava
	};
};

export const actions = {
	updateProfile: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const display_name = data.get('display_name') as string;
		const email = data.get('email') as string;

		try {
			await updateProfile(locals.token, { display_name, email });
			return { success: true, message: 'Profile updated' };
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to update profile' });
		}
	},

	changePassword: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const current_password = data.get('current_password') as string;
		const new_password = data.get('new_password') as string;
		const confirm_password = data.get('confirm_password') as string;

		if (!current_password || !new_password) {
			return fail(400, { error: 'All password fields are required' });
		}

		if (new_password !== confirm_password) {
			return fail(400, { error: 'New passwords do not match' });
		}

		if (new_password.length < 8) {
			return fail(400, { error: 'Password must be at least 8 characters' });
		}

		try {
			await changePassword(locals.token, { current_password, new_password });
			return { success: true, message: 'Password changed' };
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to change password' });
		}
	},

	updatePreferences: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const weight_unit = data.get('weight_unit') as string;
		const distance_unit = data.get('distance_unit') as string;

		try {
			await updatePreferences(locals.token, { weight_unit, distance_unit });
			return { success: true, message: 'Preferences updated' };
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to update preferences' });
		}
	},

	generateIcalToken: async ({ locals }) => {
		if (!locals.token) return fail(401);

		try {
			await apiFetch<{ ical_token: string }>('/api/export/ical-token', {
				method: 'POST',
				token: locals.token
			});
			return { success: true, message: 'Calendar feed URL generated' };
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to generate feed URL' });
		}
	},

	disconnectStrava: async ({ locals }) => {
		if (!locals.token) return fail(401);

		try {
			await disconnectStrava(locals.token);
			return { success: true, message: 'Strava disconnected' };
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to disconnect Strava' });
		}
	},

	syncStrava: async ({ locals }) => {
		if (!locals.token) return fail(401);

		try {
			const result = await syncStrava(locals.token);
			return {
				success: true,
				message: `Synced ${result.imported_count} activities (${result.skipped_count} already imported)`
			};
		} catch (e) {
			return fail(400, { error: (e as Error).message || 'Failed to sync Strava' });
		}
	}
} satisfies Actions;
