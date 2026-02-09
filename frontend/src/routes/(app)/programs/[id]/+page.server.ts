import { getProgram, deleteProgram, updateProgram } from '$lib/api/programs';
import { ApiError } from '$lib/api/client';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	try {
		const program = await getProgram(locals.token, params.id);
		return { program };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) {
			error(404, 'Program not found');
		}
		error(500, 'Failed to load program');
	}
};

export const actions = {
	delete: async ({ params, locals }) => {
		if (!locals.token) return fail(401);
		try {
			await deleteProgram(locals.token, params.id);
		} catch {
			return fail(500, { error: 'Failed to delete program' });
		}
		redirect(303, '/programs');
	},
	updateStatus: async ({ params, locals, request }) => {
		if (!locals.token) return fail(401);
		const data = await request.formData();
		const status = data.get('status') as string;
		try {
			await updateProgram(locals.token, params.id, { status });
		} catch {
			return fail(500, { error: 'Failed to update program' });
		}
	}
} satisfies Actions;
