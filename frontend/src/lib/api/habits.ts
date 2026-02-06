import { apiFetch } from './client';

export interface Habit {
	id: string;
	name: string;
	habit_type: string;
	frequency: string;
	frequency_config: Record<string, unknown>;
	target_value: number;
	unit: string | null;
	color: string;
	sort_order: number;
	is_active: boolean;
	created_at: string;
	current_streak: number;
	strength: number;
}

export interface HabitToday {
	id: string;
	name: string;
	habit_type: string;
	target_value: number;
	unit: string | null;
	color: string;
	sort_order: number;
	completed_today: boolean;
	today_value: number;
	current_streak: number;
	strength: number;
}

export interface HabitCompletion {
	id: string;
	habit_id: string;
	completed_at: string;
	value: number;
	completed: boolean;
}

export interface HabitStreak {
	current_streak: number;
	longest_streak: number;
	strength: number;
	completion_dates: string[];
}

export function getHabits(token: string) {
	return apiFetch<Habit[]>('/api/habits/', { token });
}

export function getTodayHabits(token: string) {
	return apiFetch<HabitToday[]>('/api/habits/today', { token });
}

export function createHabit(
	token: string,
	data: {
		name: string;
		habit_type: string;
		frequency?: string;
		frequency_config?: Record<string, unknown>;
		target_value?: number;
		unit?: string;
		color?: string;
	}
) {
	return apiFetch<Habit>('/api/habits/', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function updateHabit(token: string, id: string, data: Record<string, unknown>) {
	return apiFetch<Habit>(`/api/habits/${id}`, {
		method: 'PUT',
		token,
		body: JSON.stringify(data)
	});
}

export function deleteHabit(token: string, id: string) {
	return apiFetch<void>(`/api/habits/${id}`, { method: 'DELETE', token });
}

export function logCompletion(
	token: string,
	habitId: string,
	data: { value?: number; completed?: boolean } = {}
) {
	return apiFetch<HabitCompletion>(`/api/habits/${habitId}/log`, {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function removeCompletion(token: string, habitId: string, date: string) {
	return apiFetch<void>(`/api/habits/${habitId}/log/${date}`, {
		method: 'DELETE',
		token
	});
}

export function getStreak(token: string, habitId: string) {
	return apiFetch<HabitStreak>(`/api/habits/${habitId}/streak`, { token });
}
