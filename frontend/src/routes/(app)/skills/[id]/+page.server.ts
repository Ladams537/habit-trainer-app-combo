import { error, fail, redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/api/client';
import { getSkillProgress, getSkillSchedule, deleteSkill } from '$lib/api/skills';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	try {
		const [progress, schedule] = await Promise.all([
			getSkillProgress(locals.token, params.id),
			getSkillSchedule(locals.token, params.id)
		]);
		return { progress, schedule };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) {
			error(404, 'Skill not found');
		}
		error(500, 'Failed to load skill');
	}
};

export const actions = {
	delete: async ({ params, locals }) => {
		if (!locals.token) return fail(401);

		try {
			await deleteSkill(locals.token, params.id);
		} catch {
			return fail(500, { error: 'Failed to archive skill' });
		}

		redirect(303, '/skills');
	}
} satisfies Actions;
