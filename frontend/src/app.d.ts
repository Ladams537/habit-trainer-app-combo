declare global {
	namespace App {
		interface Locals {
			user: {
				id: string;
				email: string;
				display_name: string | null;
			} | null;
			token: string | null;
		}
	}
}

export {};
