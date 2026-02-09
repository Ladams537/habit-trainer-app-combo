import { redirect } from '@sveltejs/kit';
import { getStravaAuthUrl } from '$lib/api/integrations';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) redirect(302, '/login');

	const { url } = await getStravaAuthUrl(locals.token);
	redirect(302, url);
};
