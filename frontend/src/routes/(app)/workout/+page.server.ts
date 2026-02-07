import {
	getActiveSession,
	getExercises,
	getTemplate,
	logSet,
	deleteSet,
	completeSession,
	getExerciseHistory
} from '$lib/api/fitness';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.token) redirect(303, '/login');

	try {
		const [session, exercises] = await Promise.all([
			getActiveSession(locals.token),
			getExercises(locals.token)
		]);

		if (!session) {
			redirect(303, '/today');
		}

		// Get template exercises if from template
		let templateExercises: string[] = [];
		if (session.template_id) {
			try {
				const template = await getTemplate(locals.token, session.template_id);
				templateExercises = template.exercises.map((te) => te.exercise_id);
			} catch {
				// Template may have been deleted
			}
		}

		// Build exercise list: exercises already logged + template exercises
		const sessionExerciseIds = new Set(
			session.exercise_groups.map((g) => g.exercise.id)
		);
		const allWorkoutExerciseIds = new Set([...sessionExerciseIds, ...templateExercises]);

		// Get previous performance for each exercise
		const previousPerformance: Record<string, { set_number: number; weight_kg: number; reps: number }[]> = {};
		for (const exerciseId of allWorkoutExerciseIds) {
			try {
				const history = await getExerciseHistory(locals.token, exerciseId, 1);
				if (history.length > 0) {
					previousPerformance[exerciseId] = history[0].sets;
				}
			} catch {
				// Ignore
			}
		}

		return {
			session,
			exercises,
			templateExercises,
			previousPerformance
		};
	} catch {
		redirect(303, '/today');
	}
};

export const actions = {
	logSet: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const sessionId = data.get('sessionId') as string;
		const exerciseId = data.get('exerciseId') as string;
		const setNumber = parseInt(data.get('setNumber') as string);
		const weight = parseFloat(data.get('weight') as string);
		const reps = parseInt(data.get('reps') as string);

		try {
			await logSet(locals.token, sessionId, {
				exercise_id: exerciseId,
				set_number: setNumber,
				weight_kg: weight,
				reps,
				completed: true
			});
		} catch {
			return fail(500, { error: 'Failed to log set' });
		}
	},

	deleteSet: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const sessionId = data.get('sessionId') as string;
		const setId = data.get('setId') as string;

		try {
			await deleteSet(locals.token, sessionId, setId);
		} catch {
			return fail(500, { error: 'Failed to delete set' });
		}
	},

	completeWorkout: async ({ request, locals }) => {
		if (!locals.token) return fail(401);

		const data = await request.formData();
		const sessionId = data.get('sessionId') as string;
		const notes = (data.get('notes') as string) || undefined;

		try {
			await completeSession(locals.token, sessionId, notes ? { notes } : undefined);
		} catch {
			return fail(500, { error: 'Failed to complete workout' });
		}

		redirect(303, `/analytics/sessions/${sessionId}`);
	}
} satisfies Actions;
