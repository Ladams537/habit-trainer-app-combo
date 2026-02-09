declare global {
	namespace App {
		interface Locals {
			user: {
				id: string;
				email: string;
				display_name: string | null;
				preferences: Record<string, string>;
			} | null;
			token: string | null;
		}
	}
}

export {};
