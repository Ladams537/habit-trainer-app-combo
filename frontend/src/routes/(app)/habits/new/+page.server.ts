import { createHabit } from '$lib/api/habits';
import { ApiError } from '$lib/api/client';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
	default: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const name = data.get('name') as string;
		const habitType = data.get('habit_type') as string;
		const frequency = data.get('frequency') as string;
		const targetValue = parseFloat((data.get('target_value') as string) || '1');
		const unit = data.get('unit') as string;
		const color = data.get('color') as string;

		if (!name) return fail(400, { error: 'Name is required' });

		try {
			await createHabit(locals.token, {
				name,
				habit_type: habitType || 'boolean',
				frequency: frequency || 'daily',
				target_value: targetValue,
				unit: unit || undefined,
				color: color || '#4CAF50'
			});
		} catch (e) {
			if (e instanceof ApiError) {
				return fail(e.status, { error: e.message });
			}
			return fail(500, { error: 'Failed to create habit' });
		}

		redirect(303, '/today');
	}
} satisfies Actions;
