import { createSkill } from '$lib/api/skills';
import { ApiError } from '$lib/api/client';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
	default: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const name = data.get('name') as string;
		const category = data.get('category') as string;
		const subSkillsRaw = data.get('sub_skills') as string;
		const currentLevel = data.get('current_level') as string;

		if (!name) return fail(400, { error: 'Name is required' });

		const sub_skills = subSkillsRaw
			? subSkillsRaw
					.split(',')
					.map((s) => s.trim())
					.filter(Boolean)
			: [];

		try {
			await createSkill(locals.token, {
				name,
				category: category || 'general',
				sub_skills,
				current_level: currentLevel || 'beginner'
			});
		} catch (e) {
			if (e instanceof ApiError) {
				return fail(e.status, { error: e.message });
			}
			return fail(500, { error: 'Failed to create skill' });
		}

		redirect(303, '/skills');
	}
} satisfies Actions;
