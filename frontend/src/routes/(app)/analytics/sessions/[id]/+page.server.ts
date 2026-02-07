import { getSession } from '$lib/api/fitness';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
	if (!locals.token) redirect(303, '/login');

	try {
		const session = await getSession(locals.token, params.id);
		return { session };
	} catch {
		error(404, 'Session not found');
	}
};
