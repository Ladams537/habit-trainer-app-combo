import { getTodayHabits, logCompletion, removeCompletion } from '$lib/api/habits';
import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { habits: [] };

	try {
		const habits = await getTodayHabits(locals.token);
		return { habits };
	} catch {
		return { habits: [] };
	}
};

export const actions = {
	toggleHabit: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const habitId = data.get('habitId') as string;
		const completed = data.get('completed') === 'true';

		if (!habitId) return fail(400, { error: 'Missing habit ID' });

		try {
			if (completed) {
				await logCompletion(locals.token, habitId);
			} else {
				const today = new Date().toISOString().split('T')[0];
				await removeCompletion(locals.token, habitId, today);
			}
		} catch {
			return fail(500, { error: 'Failed to update habit' });
		}
	}
} satisfies Actions;
