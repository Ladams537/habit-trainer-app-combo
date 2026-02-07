import { getExercises, createTemplate } from '$lib/api/fitness';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { exercises: [] };

	try {
		const exercises = await getExercises(locals.token);
		return { exercises };
	} catch {
		return { exercises: [] };
	}
};

export const actions = {
	default: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const name = data.get('name') as string;
		const description = (data.get('description') as string) || undefined;
		const exercisesJson = data.get('exercises') as string;

		if (!name) return fail(400, { error: 'Name is required' });

		let exercises: {
			exercise_id: string;
			sort_order: number;
			target_sets: number;
			target_reps: number;
			target_weight_kg?: number;
			rest_seconds?: number;
		}[] = [];

		try {
			exercises = exercisesJson ? JSON.parse(exercisesJson) : [];
		} catch {
			return fail(400, { error: 'Invalid exercise data' });
		}

		try {
			await createTemplate(locals.token, { name, description, exercises });
		} catch {
			return fail(500, { error: 'Failed to create template' });
		}

		redirect(303, '/plan');
	}
} satisfies Actions;
