import { getExerciseProgression } from '$lib/api/fitness';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
	if (!locals.token) redirect(303, '/login');

	try {
		const stats = await getExerciseProgression(locals.token, params.id);
		return { stats };
	} catch {
		error(404, 'Exercise not found');
	}
};
