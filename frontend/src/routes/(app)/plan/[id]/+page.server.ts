import { getTemplate, getExercises, updateTemplate, deleteTemplate } from '$lib/api/fitness';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
	if (!locals.token) redirect(303, '/login');

	try {
		const [template, exercises] = await Promise.all([
			getTemplate(locals.token, params.id),
			getExercises(locals.token)
		]);
		return { template, exercises };
	} catch {
		error(404, 'Template not found');
	}
};

export const actions = {
	update: async ({ request, locals, params }) => {
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
			await updateTemplate(locals.token, params.id, { name, description, exercises });
		} catch {
			return fail(500, { error: 'Failed to update template' });
		}

		redirect(303, '/plan');
	},

	delete: async ({ locals, params }) => {
		if (!locals.token) return fail(401);

		try {
			await deleteTemplate(locals.token, params.id);
		} catch {
			return fail(500, { error: 'Failed to delete template' });
		}

		redirect(303, '/plan');
	}
} satisfies Actions;
