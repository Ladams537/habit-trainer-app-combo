import { getActiveSession, getTemplates, startSession } from '$lib/api/fitness';
import { getTodayHabits, logCompletion, removeCompletion } from '$lib/api/habits';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { habits: [], activeSession: null, templates: [] };

	try {
		const [habits, activeSession, templates] = await Promise.all([
			getTodayHabits(locals.token),
			getActiveSession(locals.token).catch(() => null),
			getTemplates(locals.token).catch(() => [])
		]);
		return { habits, activeSession, templates };
	} catch {
		return { habits: [], activeSession: null, templates: [] };
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
	},

	logHabit: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const habitId = data.get('habitId') as string;
		const value = data.get('value') as string;

		if (!habitId) return fail(400, { error: 'Missing habit ID' });
		if (!value) return fail(400, { error: 'Missing value' });

		try {
			await logCompletion(locals.token, habitId, { value: parseFloat(value) });
		} catch {
			return fail(500, { error: 'Failed to log habit' });
		}
	},

	startWorkout: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const templateId = (data.get('templateId') as string) || undefined;

		try {
			await startSession(locals.token, { template_id: templateId });
		} catch {
			return fail(500, { error: 'Failed to start workout' });
		}

		redirect(303, '/workout');
	}
} satisfies Actions;
