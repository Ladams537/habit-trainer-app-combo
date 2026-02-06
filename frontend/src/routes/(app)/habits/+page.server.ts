import { getHabits } from '$lib/api/habits';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { habits: [] };

	try {
		const habits = await getHabits(locals.token);
		return { habits };
	} catch {
		return { habits: [] };
	}
};
