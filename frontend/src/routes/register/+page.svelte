<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';

	let { form } = $props();
</script>

<div class="flex min-h-screen items-center justify-center bg-background px-4">
	<Card.Root class="w-full max-w-sm">
		<Card.Header class="text-center">
			<div class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
				<Dumbbell class="h-6 w-6 text-primary" />
			</div>
			<Card.Title class="text-2xl">Create account</Card.Title>
			<Card.Description>Set up your training tracker</Card.Description>
		</Card.Header>
		<Card.Content>
			<form method="POST" use:enhance class="space-y-4">
				{#if form?.error}
					<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
						{form.error}
					</div>
				{/if}
				<div class="space-y-2">
					<Label for="display_name">Display name</Label>
					<Input id="display_name" name="display_name" placeholder="Your name" />
				</div>
				<div class="space-y-2">
					<Label for="email">Email</Label>
					<Input id="email" name="email" type="email" required placeholder="you@example.com" />
				</div>
				<div class="space-y-2">
					<Label for="password">Password</Label>
					<Input id="password" name="password" type="password" required minlength={8} />
				</div>
				<Button type="submit" class="w-full">Create account</Button>
			</form>
		</Card.Content>
		<Card.Footer class="justify-center">
			<p class="text-sm text-muted-foreground">
				Already have an account?
				<a href="/login" class="text-primary underline-offset-4 hover:underline">Sign in</a>
			</p>
		</Card.Footer>
	</Card.Root>
</div>
