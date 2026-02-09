import { createProgram } from '$lib/api/programs';
import { getTemplates } from '$lib/api/fitness';
import { ApiError } from '$lib/api/client';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { templates: [] };
	try {
		const templates = await getTemplates(locals.token);
		return { templates };
	} catch {
		return { templates: [] };
	}
};

export const actions = {
	default: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const name = data.get('name') as string;
		const description = (data.get('description') as string) || undefined;
		const workoutsPerWeek = parseInt(data.get('workouts_per_week') as string) || 3;
		const templateIdsRaw = data.get('template_ids') as string;
		const templateIds = templateIdsRaw ? JSON.parse(templateIdsRaw) : [];

		if (!name) return fail(400, { error: 'Name is required' });

		try {
			const program = await createProgram(locals.token, {
				name,
				description,
				workouts_per_week: workoutsPerWeek,
				template_ids: templateIds
			});
			redirect(303, `/programs/${program.id}/week/1`);
		} catch (e) {
			if (e instanceof ApiError) {
				return fail(e.status, { error: e.message });
			}
			throw e;
		}
	}
} satisfies Actions;
