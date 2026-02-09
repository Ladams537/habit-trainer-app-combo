import {
	getProgram,
	updateWeekPrescriptions,
	completeWeek,
	getProgressionOptions,
	acceptProgression,
	startProgramSession
} from '$lib/api/programs';
import { ApiError } from '$lib/api/client';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	try {
		const program = await getProgram(locals.token, params.id);
		const weekNum = parseInt(params.weekNum);
		const week = program.weeks.find((w) => w.week_number === weekNum);
		if (!week) error(404, 'Week not found');

		let progressionOptions = null;
		if (week.status === 'completed') {
			try {
				progressionOptions = await getProgressionOptions(locals.token, params.id, weekNum);
			} catch {
				// No progression options available
			}
		}

		return { program, week, weekNum, progressionOptions };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) {
			error(404, 'Program not found');
		}
		throw e;
	}
};

export const actions = {
	savePrescriptions: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);
		const data = await request.formData();
		const prescriptionsRaw = data.get('prescriptions') as string;
		try {
			const prescriptions = JSON.parse(prescriptionsRaw);
			await updateWeekPrescriptions(
				locals.token,
				params.id,
				parseInt(params.weekNum),
				prescriptions
			);
		} catch (e) {
			if (e instanceof ApiError) return fail(e.status, { error: e.message });
			return fail(500, { error: 'Failed to save prescriptions' });
		}
	},
	completeWeek: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);
		const data = await request.formData();
		const recoveryRating = parseInt(data.get('recovery_rating') as string);
		const notes = (data.get('notes') as string) || undefined;
		try {
			await completeWeek(locals.token, params.id, parseInt(params.weekNum), {
				recovery_rating: recoveryRating,
				notes
			});
		} catch (e) {
			if (e instanceof ApiError) return fail(e.status, { error: e.message });
			return fail(500, { error: 'Failed to complete week' });
		}
	},
	acceptProgression: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);
		const data = await request.formData();
		const optionKey = data.get('option_key') as string;
		try {
			const nextWeek = await acceptProgression(
				locals.token,
				params.id,
				parseInt(params.weekNum),
				{ option_key: optionKey }
			);
			redirect(303, `/programs/${params.id}/week/${nextWeek.week_number}`);
		} catch (e) {
			if (e instanceof ApiError) return fail(e.status, { error: e.message });
			throw e;
		}
	},
	startSession: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);
		const data = await request.formData();
		const dayIndex = parseInt(data.get('day_index') as string);
		try {
			await startProgramSession(
				locals.token,
				params.id,
				parseInt(params.weekNum),
				dayIndex
			);
			redirect(303, '/workout');
		} catch (e) {
			if (e instanceof ApiError) return fail(e.status, { error: e.message });
			throw e;
		}
	}
} satisfies Actions;
