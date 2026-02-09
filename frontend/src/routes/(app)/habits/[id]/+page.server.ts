import { error, fail, redirect } from '@sveltejs/kit';
import { apiFetch, ApiError } from '$lib/api/client';
import { getStreak, deleteHabit, updateHabit } from '$lib/api/habits';
import type { Habit, HabitStreak } from '$lib/api/habits';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	try {
		const [habit, streak] = await Promise.all([
			apiFetch<Habit>(`/api/habits/${params.id}`, { token: locals.token }),
			getStreak(locals.token, params.id)
		]);
		return { habit, streak };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) {
			error(404, 'Habit not found');
		}
		error(500, 'Failed to load habit');
	}
};

export const actions = {
	delete: async ({ params, locals }) => {
		if (!locals.token) return fail(401);

		try {
			await deleteHabit(locals.token, params.id);
		} catch {
			return fail(500, { error: 'Failed to delete habit' });
		}

		redirect(303, '/habits');
	},
	updatePartial: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const partialCompletionCounts = (data.get('partial_completion_counts') as string) === 'true';

		try {
			await updateHabit(locals.token, params.id, {
				partial_completion_counts: partialCompletionCounts
			});
		} catch {
			return fail(500, { error: 'Failed to update habit' });
		}
	}
} satisfies Actions;
