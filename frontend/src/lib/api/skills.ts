import { apiFetch } from './client';

// --- Types ---

export interface Skill {
	id: string;
	user_id: string;
	name: string;
	category: string;
	sub_skills: string[];
	current_level: string;
	total_practice_minutes: number;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface PracticeSession {
	id: string;
	skill_id: string;
	duration_minutes: number;
	quality_rating: number;
	focus_area: string | null;
	notes: string | null;
	practiced_at: string;
}

export interface CompetencyLevel {
	id: string;
	skill_id: string;
	sub_skill: string;
	difficulty: number;
	stability: number;
	last_review_date: string | null;
	next_review_date: string | null;
	review_count: number;
	retrievability: number;
}

export interface SkillProgress {
	skill: Skill;
	competency_levels: CompetencyLevel[];
	recent_sessions: PracticeSession[];
}

export interface SubSkillSchedule {
	sub_skill: string;
	next_review_date: string | null;
	retrievability: number;
	is_due: boolean;
}

export interface SkillSchedule {
	skill: Skill;
	schedule: SubSkillSchedule[];
}

export interface SkillToday {
	id: string;
	name: string;
	category: string;
	due_count: number;
	total_practice_minutes: number;
}

// --- Skills CRUD ---

export function getSkills(token: string) {
	return apiFetch<Skill[]>('/api/skills/', { token });
}

export function getSkill(token: string, id: string) {
	return apiFetch<Skill>(`/api/skills/${id}`, { token });
}

export function createSkill(
	token: string,
	data: { name: string; category?: string; sub_skills?: string[]; current_level?: string }
) {
	return apiFetch<Skill>('/api/skills/', {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

export function updateSkill(
	token: string,
	id: string,
	data: { name?: string; category?: string; sub_skills?: string[]; current_level?: string }
) {
	return apiFetch<Skill>(`/api/skills/${id}`, {
		method: 'PUT',
		token,
		body: JSON.stringify(data)
	});
}

export function deleteSkill(token: string, id: string) {
	return apiFetch<void>(`/api/skills/${id}`, { method: 'DELETE', token });
}

// --- Practice ---

export function logPractice(
	token: string,
	skillId: string,
	data: {
		duration_minutes: number;
		quality_rating: number;
		focus_area?: string;
		notes?: string;
	}
) {
	return apiFetch<PracticeSession>(`/api/skills/${skillId}/practice`, {
		method: 'POST',
		token,
		body: JSON.stringify(data)
	});
}

// --- Progress / Schedule / Today ---

export function getSkillProgress(token: string, skillId: string) {
	return apiFetch<SkillProgress>(`/api/skills/${skillId}/progress`, { token });
}

export function getSkillSchedule(token: string, skillId: string) {
	return apiFetch<SkillSchedule>(`/api/skills/${skillId}/schedule`, { token });
}

export function getSkillsDueToday(token: string) {
	return apiFetch<SkillToday[]>('/api/skills/today', { token });
}
