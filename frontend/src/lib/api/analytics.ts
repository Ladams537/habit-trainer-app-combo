import { apiFetch } from './client';

// --- Types ---

export interface HeatmapDay {
	date: string;
	count: number;
	fitness_count: number;
	habits_count: number;
	skills_count: number;
}

export interface HeatmapResponse {
	year: number;
	days: HeatmapDay[];
}

export interface StreakItem {
	domain: string;
	name: string;
	current_streak: number;
	longest_streak: number;
	strength: number | null;
	entity_id: string | null;
}

export interface StreaksResponse {
	streaks: StreakItem[];
	total_active: number;
}

export interface TrendPoint {
	date: string;
	value: number;
}

export interface TrendSeries {
	metric: string;
	unit: string;
	data: TrendPoint[];
}

export interface TrendsResponse {
	domain: string;
	period_days: number;
	series: TrendSeries[];
}

export interface CorrelationPoint {
	date: string;
	x_value: number;
	y_value: number;
}

export interface CorrelationResponse {
	x_label: string;
	y_label: string;
	correlation_coefficient: number | null;
	data: CorrelationPoint[];
}

export interface InsightCard {
	id: string;
	icon: string;
	domain: string;
	color: string;
	title: string;
	message: string;
}

export interface AnalyticsDashboardResponse {
	insights: InsightCard[];
	heatmap: HeatmapResponse;
	streaks: StreaksResponse;
}

// --- Calendar ---

export interface CalendarEvent {
	date: string;
	domain: string;
	event_type: string;
	entity_id: string | null;
	title: string;
	subtitle: string | null;
	color: string | null;
	metadata: Record<string, unknown> | null;
}

export interface CalendarDay {
	date: string;
	events: CalendarEvent[];
}

export interface CalendarResponse {
	from_date: string;
	to_date: string;
	days: CalendarDay[];
}

// --- API Functions ---

export function getDashboard(token: string) {
	return apiFetch<AnalyticsDashboardResponse>('/api/analytics/dashboard', { token });
}

export function getHeatmap(token: string, year?: number) {
	const params = year ? `?year=${year}` : '';
	return apiFetch<HeatmapResponse>(`/api/analytics/heatmap${params}`, { token });
}

export function getStreaks(token: string) {
	return apiFetch<StreaksResponse>('/api/analytics/streaks', { token });
}

export function getTrends(token: string, domain: string, period = '90d') {
	return apiFetch<TrendsResponse>(
		`/api/analytics/trends?domain=${domain}&period=${period}`,
		{ token }
	);
}

export function getCalendar(token: string, from: string, to: string) {
	return apiFetch<CalendarResponse>(
		`/api/analytics/calendar?from=${from}&to=${to}`,
		{ token }
	);
}

export function getCorrelations(
	token: string,
	x = 'habits.completion_rate',
	y = 'fitness.volume',
	period = '90d'
) {
	return apiFetch<CorrelationResponse>(
		`/api/analytics/correlations?x=${encodeURIComponent(x)}&y=${encodeURIComponent(y)}&period=${period}`,
		{ token }
	);
}
