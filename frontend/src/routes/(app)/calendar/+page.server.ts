import { getCalendar } from '$lib/api/analytics';
import { getWeeklySummaries } from '$lib/api/programs';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
	if (!locals.token) return { calendar: null, weeklySummaries: [] };

	const now = new Date();
	const yearParam = url.searchParams.get('year');
	const monthParam = url.searchParams.get('month');

	const year = yearParam ? parseInt(yearParam) : now.getFullYear();
	const month = monthParam ? parseInt(monthParam) : now.getMonth() + 1;

	const firstDay = `${year}-${String(month).padStart(2, '0')}-01`;
	const lastDayDate = new Date(year, month, 0);
	const lastDay = `${year}-${String(month).padStart(2, '0')}-${String(lastDayDate.getDate()).padStart(2, '0')}`;

	try {
		const [calendar, weeklySummaries] = await Promise.all([
			getCalendar(locals.token, firstDay, lastDay),
			getWeeklySummaries(locals.token, 4).catch(() => [])
		]);
		return { calendar, weeklySummaries, year, month };
	} catch {
		return { calendar: null, weeklySummaries: [], year, month };
	}
};
