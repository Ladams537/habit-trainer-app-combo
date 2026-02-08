import { apiFetch } from './client';

// --- Types ---

export interface Exercise {
	id: string;
	user_id: string | null;
	name: string;
	category: string;
	muscle_groups: string[];
	equipment: string | null;
	is_custom: boolean;
	created_at: string;
}

export interface TemplateExercise {
	id: string;
	exercise_id: string;
	sort_order: number;
	target_sets: number;
	target_reps: number;
	target_weight_kg: number | null;
	set_type: string;
	rest_seconds: number;
	exercise: Exercise;
}

export interface WorkoutTemplate {
	id: string;
	user_id: string;
	name: string;
	description: string | null;
	created_at: string;
	updated_at: string;
	exercises: TemplateExercise[];
}

export interface WorkoutSet {
	id: string;
	session_id: string;
	exercise_id: string;
	set_number: number;
	weight_kg: number;
	reps: number;
	rpe: number | null;
	set_type: string;
	completed: boolean;
	logged_at: string;
}

export interface ExerciseSetsGroup {
	exercise: Exercise;
	sets: WorkoutSet[];
}

export interface WorkoutSession {
	id: string;
	user_id: string;
	template_id: string | null;
	started_at: string;
	completed_at: string | null;
	notes: string | null;
	status: string;
	template_name: string | null;
	exercise_groups: ExerciseSetsGroup[];
	rating_energy: number | null;
	rating_mood: number | null;
}

export interface WorkoutSessionSummary {
	id: string;
	template_id: string | null;
	started_at: string;
	completed_at: string | null;
	status: string;
	template_name: string | null;
	exercise_count: number;
	total_sets: number;
	total_volume: number;
	rating_energy: number | null;
	rating_mood: number | null;
}

export interface ExerciseProgressionPoint {
	date: string;
	max_weight: number;
	best_set_weight: number;
	best_set_reps: number;
	volume: number;
	sets_count: number;
	estimated_1rm: number;
}

export interface ExerciseStats {
	exercise: Exercise;
	progression: ExerciseProgressionPoint[];
	total_sessions: number;
	pr_weight: number;
	total_volume: number;
}

export interface PreviousSet {
	set_number: number;
	weight_kg: number;
	reps: number;
}

export interface WeeklyVolume {
	week_start: string;
	total_volume: number;
	session_count: number;
}

export interface MuscleGroupVolume {
	muscle_group: string;
	volume: number;
}

export interface OverviewStats {
	weekly_volume: WeeklyVolume[];
	muscle_group_volume: MuscleGroupVolume[];
	total_workouts: number;
	total_volume: number;
	current_streak: number;
}

// --- Exercises ---

export function getExercises(token: string, params?: { category?: string; muscle_group?: string }) {
	const searchParams = new URLSearchParams();
	if (params?.category) searchParams.set('category', params.category);
	if (params?.muscle_group) searchParams.set('muscle_group', params.muscle_group);
	const qs = searchParams.toString();
	return apiFetch<Exercise[]>(`/api/fitness/exercises${qs ? `?${qs}` : ''}`, { token });
}

export function createExercise(
	token: string,
	data: { name: string; category: string; muscle_groups?: string[]; equipment?: string }
) {
	return apiFetch<Exercise>('/api/fitness/exercises', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

// --- Templates ---

export function getTemplates(token: string) {
	return apiFetch<WorkoutTemplate[]>('/api/fitness/templates', { token });
}

export function getTemplate(token: string, id: string) {
	return apiFetch<WorkoutTemplate>(`/api/fitness/templates/${id}`, { token });
}

export function createTemplate(
	token: string,
	data: {
		name: string;
		description?: string;
		exercises: {
			exercise_id: string;
			sort_order: number;
			target_sets: number;
			target_reps: number;
			target_weight_kg?: number;
			rest_seconds?: number;
		}[];
	}
) {
	return apiFetch<WorkoutTemplate>('/api/fitness/templates', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function updateTemplate(
	token: string,
	id: string,
	data: {
		name?: string;
		description?: string;
		exercises?: {
			exercise_id: string;
			sort_order: number;
			target_sets: number;
			target_reps: number;
			target_weight_kg?: number;
			rest_seconds?: number;
		}[];
	}
) {
	return apiFetch<WorkoutTemplate>(`/api/fitness/templates/${id}`, {
		method: 'PUT',
		token,
		body: JSON.stringify(data)
	});
}

export function deleteTemplate(token: string, id: string) {
	return apiFetch<void>(`/api/fitness/templates/${id}`, { method: 'DELETE', token });
}

// --- Sessions ---

export function startSession(token: string, data: { template_id?: string } = {}) {
	return apiFetch<WorkoutSession>('/api/fitness/sessions/start', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function getActiveSession(token: string) {
	return apiFetch<WorkoutSession | null>('/api/fitness/sessions/active', { token });
}

export function getSession(token: string, id: string) {
	return apiFetch<WorkoutSession>(`/api/fitness/sessions/${id}`, { token });
}

export function getSessions(token: string, params?: { limit?: number; offset?: number }) {
	const searchParams = new URLSearchParams();
	if (params?.limit) searchParams.set('limit', params.limit.toString());
	if (params?.offset) searchParams.set('offset', params.offset.toString());
	const qs = searchParams.toString();
	return apiFetch<WorkoutSessionSummary[]>(
		`/api/fitness/sessions${qs ? `?${qs}` : ''}`,
		{ token }
	);
}

export function logSet(
	token: string,
	sessionId: string,
	data: {
		exercise_id: string;
		set_number: number;
		weight_kg: number;
		reps: number;
		rpe?: number;
		set_type?: string;
		completed?: boolean;
	}
) {
	return apiFetch<WorkoutSet>(`/api/fitness/sessions/${sessionId}/sets`, {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function deleteSet(token: string, sessionId: string, setId: string) {
	return apiFetch<void>(`/api/fitness/sessions/${sessionId}/sets/${setId}`, {
		method: 'DELETE',
		token
	});
}

export function addExerciseToSession(token: string, sessionId: string, exerciseId: string) {
	return apiFetch<void>(`/api/fitness/sessions/${sessionId}/exercises`, {
		method: 'POST',
		token,
		body: JSON.stringify({ exercise_id: exerciseId })
	});
}

export function completeSession(
	token: string,
	sessionId: string,
	data?: { notes?: string; rating_energy?: number; rating_mood?: number }
) {
	return apiFetch<WorkoutSession>(`/api/fitness/sessions/${sessionId}/complete`, {
		method: 'POST',
		token,
		body: data ? JSON.stringify(data) : undefined
	});
}

// --- Stats ---

export function getExerciseHistory(token: string, exerciseId: string, limit = 10) {
	return apiFetch<{ session_id: string; sets: PreviousSet[] }[]>(
		`/api/fitness/exercises/${exerciseId}/history?limit=${limit}`,
		{ token }
	);
}

export function getExerciseProgression(
	token: string,
	exerciseId: string,
	params?: { from_date?: string; to_date?: string }
) {
	const searchParams = new URLSearchParams();
	if (params?.from_date) searchParams.set('from_date', params.from_date);
	if (params?.to_date) searchParams.set('to_date', params.to_date);
	const qs = searchParams.toString();
	return apiFetch<ExerciseStats>(
		`/api/fitness/exercises/${exerciseId}/progression${qs ? `?${qs}` : ''}`,
		{ token }
	);
}

export function getTrainedExercises(token: string) {
	return apiFetch<Exercise[]>('/api/fitness/stats/trained-exercises', { token });
}

export function getOverviewStats(
	token: string,
	params?: { from_date?: string; to_date?: string }
) {
	const searchParams = new URLSearchParams();
	if (params?.from_date) searchParams.set('from_date', params.from_date);
	if (params?.to_date) searchParams.set('to_date', params.to_date);
	const qs = searchParams.toString();
	return apiFetch<OverviewStats>(
		`/api/fitness/stats/overview${qs ? `?${qs}` : ''}`,
		{ token }
	);
}
