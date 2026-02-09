import { getPrograms } from '$lib/api/programs';
import { getTemplates } from '$lib/api/fitness';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { programs: [], templates: [] };

	try {
		const [programs, templates] = await Promise.all([
			getPrograms(locals.token).catch(() => []),
			getTemplates(locals.token).catch(() => [])
		]);
		return { programs, templates };
	} catch {
		return { programs: [], templates: [] };
	}
};
