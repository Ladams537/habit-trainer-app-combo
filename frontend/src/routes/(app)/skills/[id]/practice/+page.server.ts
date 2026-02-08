import { error, fail, redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/api/client';
import { getSkill, getSkillSchedule, logPractice } from '$lib/api/skills';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	try {
		const [skill, schedule] = await Promise.all([
			getSkill(locals.token, params.id),
			getSkillSchedule(locals.token, params.id)
		]);
		return { skill, schedule };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) {
			error(404, 'Skill not found');
		}
		error(500, 'Failed to load skill');
	}
};

export const actions = {
	default: async ({ request, params, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const durationMinutes = parseInt(data.get('duration_minutes') as string, 10);
		const qualityRating = parseInt(data.get('quality_rating') as string, 10);
		const focusArea = (data.get('focus_area') as string) || undefined;
		const notes = (data.get('notes') as string) || undefined;

		if (!durationMinutes || durationMinutes < 1) {
			return fail(400, { error: 'Duration must be at least 1 minute' });
		}
		if (!qualityRating || qualityRating < 1 || qualityRating > 5) {
			return fail(400, { error: 'Please rate your practice quality (1-5)' });
		}

		try {
			await logPractice(locals.token, params.id, {
				duration_minutes: durationMinutes,
				quality_rating: qualityRating,
				focus_area: focusArea,
				notes
			});
		} catch (e) {
			if (e instanceof ApiError) {
				return fail(e.status, { error: e.message });
			}
			return fail(500, { error: 'Failed to log practice' });
		}

		redirect(303, `/skills/${params.id}`);
	}
} satisfies Actions;
