import { apiFetch } from './client';

// --- Types ---

export interface ProgramExercisePrescription {
	exercise_id: string;
	exercise_name: string;
	sets: number;
	reps: number;
	weight_kg: number;
	rest_seconds: number;
	set_type: string;
}

export interface ProgramDayPrescription {
	day_label: string;
	template_id: string | null;
	exercises: ProgramExercisePrescription[];
}

export interface ProgramWeek {
	id: string;
	week_number: number;
	status: string;
	prescriptions: ProgramDayPrescription[];
	progression_source: string | null;
	recovery_rating: number | null;
	notes: string | null;
	completed_at: string | null;
	created_at: string;
}

export interface Program {
	id: string;
	name: string;
	description: string | null;
	status: string;
	workouts_per_week: number;
	weeks: ProgramWeek[];
	created_at: string;
	updated_at: string;
}

export interface ProgramSummary {
	id: string;
	name: string;
	status: string;
	workouts_per_week: number;
	week_count: number;
	current_week: number | null;
	created_at: string;
}

export interface ProgressionOption {
	label: string;
	key: string;
	prescriptions: ProgramDayPrescription[];
	description: string;
}

export interface ProgressionOptionsResponse {
	week_number: number;
	options: ProgressionOption[];
}

export interface WeeklySummary {
	week_start: string;
	session_count: number;
	total_volume: number;
	exercises_trained: string[];
	avg_rpe: number | null;
	avg_energy: number | null;
}

// --- API Functions ---

export function getPrograms(token: string, status?: string) {
	const params = status ? `?status=${status}` : '';
	return apiFetch<ProgramSummary[]>(`/api/fitness/programs${params}`, { token });
}

export function getProgram(token: string, id: string) {
	return apiFetch<Program>(`/api/fitness/programs/${id}`, { token });
}

export function createProgram(
	token: string,
	data: {
		name: string;
		description?: string;
		workouts_per_week: number;
		template_ids: string[];
	}
) {
	return apiFetch<Program>('/api/fitness/programs', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function updateProgram(
	token: string,
	id: string,
	data: { name?: string; description?: string; status?: string }
) {
	return apiFetch<Program>(`/api/fitness/programs/${id}`, {
		method: 'PUT',
		token,
		body: JSON.stringify(data)
	});
}

export function deleteProgram(token: string, id: string) {
	return apiFetch<void>(`/api/fitness/programs/${id}`, { method: 'DELETE', token });
}

export function updateWeekPrescriptions(
	token: string,
	programId: string,
	weekNum: number,
	prescriptions: ProgramDayPrescription[]
) {
	return apiFetch<ProgramWeek>(
		`/api/fitness/programs/${programId}/weeks/${weekNum}`,
		{
			method: 'PUT',
			token,
			body: JSON.stringify(prescriptions)
		}
	);
}

export function completeWeek(
	token: string,
	programId: string,
	weekNum: number,
	data: { recovery_rating: number; notes?: string }
) {
	return apiFetch<ProgramWeek>(
		`/api/fitness/programs/${programId}/weeks/${weekNum}/complete`,
		{
			method: 'POST',
			token,
			body: JSON.stringify(data)
		}
	);
}

export function getProgressionOptions(token: string, programId: string, weekNum: number) {
	return apiFetch<ProgressionOptionsResponse>(
		`/api/fitness/programs/${programId}/weeks/${weekNum}/progression`,
		{ token }
	);
}

export function acceptProgression(
	token: string,
	programId: string,
	weekNum: number,
	data: { option_key: string; tweaks?: ProgramDayPrescription[] }
) {
	return apiFetch<ProgramWeek>(
		`/api/fitness/programs/${programId}/weeks/${weekNum}/progression`,
		{
			method: 'POST',
			token,
			body: JSON.stringify(data)
		}
	);
}

export function startProgramSession(
	token: string,
	programId: string,
	weekNum: number,
	dayIndex: number
) {
	return apiFetch<import('./fitness').WorkoutSession>(
		`/api/fitness/programs/${programId}/weeks/${weekNum}/start-session?day_index=${dayIndex}`,
		{ method: 'POST', token }
	);
}

export function getWeeklySummaries(token: string, weeks = 12) {
	return apiFetch<WeeklySummary[]>(
		`/api/fitness/stats/weekly-summaries?weeks=${weeks}`,
		{ token }
	);
}
