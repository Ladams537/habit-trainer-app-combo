import { getOverviewStats, getSessions, getTrainedExercises } from '$lib/api/fitness';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) return { sessions: [], overview: null, trainedExercises: [] };

	try {
		const [sessions, overview, trainedExercises] = await Promise.all([
			getSessions(locals.token, { limit: 50 }),
			getOverviewStats(locals.token).catch(() => null),
			getTrainedExercises(locals.token).catch(() => [])
		]);
		return { sessions, overview, trainedExercises };
	} catch {
		return { sessions: [], overview: null, trainedExercises: [] };
	}
};
