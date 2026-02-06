import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { apiFetch, ApiError } from '$lib/api/client';

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.user) {
		redirect(302, '/today');
	}
};

export const actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const email = data.get('email') as string;
		const password = data.get('password') as string;
		const displayName = data.get('display_name') as string;

		if (!email || !password) {
			return fail(400, { error: 'Email and password are required' });
		}

		try {
			await apiFetch('/api/auth/register', {
				method: 'POST',
				body: JSON.stringify({
					email,
					password,
					display_name: displayName || null
				})
			});

			// Auto-login after registration
			const formBody = new URLSearchParams();
			formBody.set('username', email);
			formBody.set('password', password);

			const tokens = await apiFetch<{ access_token: string; refresh_token: string }>(
				'/api/auth/login',
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
					body: formBody.toString()
				}
			);

			cookies.set('access_token', tokens.access_token, {
				path: '/',
				httpOnly: true,
				sameSite: 'lax',
				secure: false,
				maxAge: 60 * 15
			});

			cookies.set('refresh_token', tokens.refresh_token, {
				path: '/',
				httpOnly: true,
				sameSite: 'lax',
				secure: false,
				maxAge: 60 * 60 * 24 * 7
			});
		} catch (e) {
			if (e instanceof ApiError) {
				return fail(e.status, { error: e.message });
			}
			return fail(500, { error: 'An unexpected error occurred' });
		}

		redirect(303, '/today');
	}
} satisfies Actions;
