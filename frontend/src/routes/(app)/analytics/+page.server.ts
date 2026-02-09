import { getDashboard, getTrends, getCorrelations } from '$lib/api/analytics';
import { getOverviewStats, getTrainedExercises } from '$lib/api/fitness';
import { getWeeklySummaries } from '$lib/api/programs';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token)
		return {
			weeklySummaries: [],
			overview: null,
			trainedExercises: [],
			dashboard: null,
			habitsTrends: null,
			skillsTrends: null,
			correlations: null
		};

	try {
		const [weeklySummaries, overview, trainedExercises, dashboard, habitsTrends, skillsTrends, correlations] =
			await Promise.all([
				getWeeklySummaries(locals.token, 12).catch(() => []),
				getOverviewStats(locals.token).catch(() => null),
				getTrainedExercises(locals.token).catch(() => []),
				getDashboard(locals.token).catch(() => null),
				getTrends(locals.token, 'habits', '90d').catch(() => null),
				getTrends(locals.token, 'skills', '90d').catch(() => null),
				getCorrelations(locals.token).catch(() => null)
			]);
		return {
			weeklySummaries,
			overview,
			trainedExercises,
			dashboard,
			habitsTrends,
			skillsTrends,
			correlations
		};
	} catch {
		return {
			weeklySummaries: [],
			overview: null,
			trainedExercises: [],
			dashboard: null,
			habitsTrends: null,
			skillsTrends: null,
			correlations: null
		};
	}
};
