import type { Handle } from '@sveltejs/kit';
import { apiFetch } from '$lib/api/client';

export const handle: Handle = async ({ event, resolve }) => {
	const accessToken = event.cookies.get('access_token');
	const refreshToken = event.cookies.get('refresh_token');

	event.locals.user = null;
	event.locals.token = null;

	if (accessToken) {
		try {
			const user = await apiFetch<App.Locals['user']>('/api/auth/me', {
				token: accessToken
			});
			event.locals.user = user;
			event.locals.token = accessToken;
		} catch {
			if (refreshToken) {
				try {
					const { access_token } = await apiFetch<{ access_token: string }>(
						'/api/auth/refresh',
						{
							method: 'POST',
							body: JSON.stringify({ refresh_token: refreshToken })
						}
					);
					event.cookies.set('access_token', access_token, {
						path: '/',
						httpOnly: true,
						sameSite: 'lax',
						secure: false,
						maxAge: 60 * 15
					});

					const user = await apiFetch<App.Locals['user']>('/api/auth/me', {
						token: access_token
					});
					event.locals.user = user;
					event.locals.token = access_token;
				} catch {
					event.cookies.delete('access_token', { path: '/' });
					event.cookies.delete('refresh_token', { path: '/' });
				}
			}
		}
	}

	return resolve(event);
};
