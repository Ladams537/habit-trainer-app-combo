import { env } from '$env/dynamic/private';
import { error, redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const API_BASE = env.API_URL || 'http://localhost:8000';

const VALID_TYPES = ['workouts', 'habits', 'skills', 'backup'] as const;

export const GET: RequestHandler = async ({ params, locals }) => {
	if (!locals.token) redirect(302, '/login');

	const type = params.type;
	if (!VALID_TYPES.includes(type as (typeof VALID_TYPES)[number])) {
		error(404, 'Invalid export type');
	}

	const res = await fetch(`${API_BASE}/api/export/${type}`, {
		headers: {
			Authorization: `Bearer ${locals.token}`
		}
	});

	if (!res.ok) {
		error(res.status, 'Export failed');
	}

	const contentType = res.headers.get('content-type') || 'application/octet-stream';
	const disposition = res.headers.get('content-disposition') || '';

	return new Response(res.body, {
		headers: {
			'Content-Type': contentType,
			'Content-Disposition': disposition
		}
	});
};
