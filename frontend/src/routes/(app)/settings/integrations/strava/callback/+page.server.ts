import { redirect, fail } from '@sveltejs/kit';
import { connectStrava } from '$lib/api/integrations';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals }) => {
	if (!locals.token) redirect(302, '/login');

	const code = url.searchParams.get('code');
	const error = url.searchParams.get('error');

	if (error) {
		redirect(303, '/settings?error=strava_denied');
	}

	if (!code) {
		redirect(303, '/settings?error=strava_no_code');
	}

	try {
		await connectStrava(locals.token, code);
	} catch {
		redirect(303, '/settings?error=strava_connect_failed');
	}

	redirect(303, '/settings');
};
