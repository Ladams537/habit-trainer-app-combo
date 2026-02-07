import { getTemplates, deleteTemplate } from '$lib/api/fitness';
import { fail } from '@sveltejs/kit';
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
	deleteTemplate: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const templateId = data.get('templateId') as string;

		if (!templateId) return fail(400, { error: 'Missing template ID' });

		try {
			await deleteTemplate(locals.token, templateId);
		} catch {
			return fail(500, { error: 'Failed to delete template' });
		}
	}
} satisfies Actions;
