import { getSkills } from '$lib/api/skills';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { skills: [] };

	try {
		const skills = await getSkills(locals.token);
		return { skills };
	} catch {
		return { skills: [] };
	}
};
