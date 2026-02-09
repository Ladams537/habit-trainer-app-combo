<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import User from '@lucide/svelte/icons/user';
	import Lock from '@lucide/svelte/icons/lock';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';
	import Download from '@lucide/svelte/icons/download';
	import Calendar from '@lucide/svelte/icons/calendar';
	import Link2 from '@lucide/svelte/icons/link-2';
	import Check from '@lucide/svelte/icons/check';

	let { data, form } = $props();

	let profileSaving = $state(false);
	let passwordSaving = $state(false);
	let prefsSaving = $state(false);
	let showSuccess = $state<string | null>(null);

	function flashSuccess(msg: string) {
		showSuccess = msg;
		setTimeout(() => (showSuccess = null), 3000);
	}

	$effect(() => {
		if (form?.success && form?.message) {
			flashSuccess(form.message);
		}
	});
</script>

<div class="mx-auto max-w-2xl space-y-6">
	<h1 class="text-2xl font-bold">Settings</h1>

	{#if showSuccess}
		<div
			class="flex items-center gap-2 rounded-lg border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-400"
		>
			<Check class="h-4 w-4" />
			{showSuccess}
		</div>
	{/if}

	{#if form?.error}
		<div
			class="rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive"
		>
			{form.error}
		</div>
	{/if}

	<!-- Profile -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<User class="h-4 w-4" />
				Profile
			</Card.Title>
		</Card.Header>
		<Card.Content>
			<form
				method="POST"
				action="?/updateProfile"
				use:enhance={() => {
					profileSaving = true;
					return async ({ update }) => {
						profileSaving = false;
						await update();
					};
				}}
				class="space-y-4"
			>
				<div class="space-y-2">
					<Label for="display_name">Display name</Label>
					<Input
						id="display_name"
						name="display_name"
						value={data.user?.display_name ?? ''}
						placeholder="Your name"
					/>
				</div>
				<div class="space-y-2">
					<Label for="email">Email</Label>
					<Input
						id="email"
						name="email"
						type="email"
						value={data.user?.email ?? ''}
						required
					/>
				</div>
				<Button type="submit" size="sm" disabled={profileSaving}>
					{profileSaving ? 'Saving...' : 'Save profile'}
				</Button>
			</form>
		</Card.Content>
	</Card.Root>

	<!-- Password -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<Lock class="h-4 w-4" />
				Change Password
			</Card.Title>
		</Card.Header>
		<Card.Content>
			<form
				method="POST"
				action="?/changePassword"
				use:enhance={() => {
					passwordSaving = true;
					return async ({ update }) => {
						passwordSaving = false;
						await update({ reset: true });
					};
				}}
				class="space-y-4"
			>
				<div class="space-y-2">
					<Label for="current_password">Current password</Label>
					<Input
						id="current_password"
						name="current_password"
						type="password"
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="new_password">New password</Label>
					<Input
						id="new_password"
						name="new_password"
						type="password"
						required
						minlength={8}
					/>
				</div>
				<div class="space-y-2">
					<Label for="confirm_password">Confirm new password</Label>
					<Input
						id="confirm_password"
						name="confirm_password"
						type="password"
						required
						minlength={8}
					/>
				</div>
				<Button type="submit" size="sm" disabled={passwordSaving}>
					{passwordSaving ? 'Changing...' : 'Change password'}
				</Button>
			</form>
		</Card.Content>
	</Card.Root>

	<!-- Preferences -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<SlidersHorizontal class="h-4 w-4" />
				Preferences
			</Card.Title>
		</Card.Header>
		<Card.Content>
			<form
				method="POST"
				action="?/updatePreferences"
				use:enhance={() => {
					prefsSaving = true;
					return async ({ update }) => {
						prefsSaving = false;
						await update();
					};
				}}
				class="space-y-4"
			>
				<div class="space-y-2">
					<Label for="weight_unit">Weight unit</Label>
					<select
						id="weight_unit"
						name="weight_unit"
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
						value={data.user?.preferences?.weight_unit ?? 'kg'}
					>
						<option value="kg">Kilograms (kg)</option>
						<option value="lbs">Pounds (lbs)</option>
					</select>
				</div>
				<div class="space-y-2">
					<Label for="distance_unit">Distance unit</Label>
					<select
						id="distance_unit"
						name="distance_unit"
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
						value={data.user?.preferences?.distance_unit ?? 'km'}
					>
						<option value="km">Kilometers (km)</option>
						<option value="mi">Miles (mi)</option>
					</select>
				</div>
				<Button type="submit" size="sm" disabled={prefsSaving}>
					{prefsSaving ? 'Saving...' : 'Save preferences'}
				</Button>
			</form>
		</Card.Content>
	</Card.Root>

	<!-- Data Export (wired in Step 2) -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<Download class="h-4 w-4" />
				Data Export
			</Card.Title>
			<Card.Description>Download your data as CSV or full JSON backup</Card.Description>
		</Card.Header>
		<Card.Content>
			<div class="flex flex-wrap gap-2">
				<Button variant="outline" size="sm" href="/settings/export/workouts">
					<Download class="mr-1.5 h-3.5 w-3.5" />
					Workouts CSV
				</Button>
				<Button variant="outline" size="sm" href="/settings/export/habits">
					<Download class="mr-1.5 h-3.5 w-3.5" />
					Habits CSV
				</Button>
				<Button variant="outline" size="sm" href="/settings/export/skills">
					<Download class="mr-1.5 h-3.5 w-3.5" />
					Skills CSV
				</Button>
				<Button variant="outline" size="sm" href="/settings/export/backup">
					<Download class="mr-1.5 h-3.5 w-3.5" />
					Full Backup (JSON)
				</Button>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Calendar Feed (wired in Step 3) -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<Calendar class="h-4 w-4" />
				Calendar Feed
			</Card.Title>
			<Card.Description>Subscribe in Apple Calendar, Google Calendar, etc.</Card.Description>
		</Card.Header>
		<Card.Content>
			{#if data.user?.preferences?.ical_token}
				<div class="space-y-3">
					<div class="flex items-center gap-2">
						<Input
							readonly
							value="{typeof window !== 'undefined' ? window.location.origin : ''}/api/ical/{data.user.preferences.ical_token}.ics"
							class="font-mono text-xs"
						/>
						<Button
							variant="outline"
							size="sm"
							onclick={() => {
								const url = `${window.location.origin}/api/ical/${data.user?.preferences?.ical_token}.ics`;
								navigator.clipboard.writeText(url);
								flashSuccess('Feed URL copied');
							}}
						>
							Copy
						</Button>
					</div>
					<form method="POST" action="?/generateIcalToken" use:enhance>
						<Button variant="ghost" size="sm" type="submit">Regenerate URL</Button>
					</form>
				</div>
			{:else}
				<form method="POST" action="?/generateIcalToken" use:enhance>
					<Button variant="outline" size="sm" type="submit">
						<Calendar class="mr-1.5 h-3.5 w-3.5" />
						Generate feed URL
					</Button>
				</form>
			{/if}
		</Card.Content>
	</Card.Root>

	<!-- Integrations (wired in Step 5) -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center gap-2">
				<Link2 class="h-4 w-4" />
				Integrations
			</Card.Title>
			<Card.Description>Connect external services</Card.Description>
		</Card.Header>
		<Card.Content>
			<div
				class="flex items-center justify-between rounded-lg border border-border px-4 py-3"
			>
				<div>
					<p class="font-medium text-sm">Strava</p>
					<p class="text-xs text-muted-foreground">Import runs, rides, and other activities</p>
				</div>
				{#if data.strava?.connected}
					<div class="flex items-center gap-2">
						<span class="text-xs text-green-400">Connected</span>
						<form method="POST" action="?/disconnectStrava" use:enhance>
							<Button variant="ghost" size="sm" type="submit">Disconnect</Button>
						</form>
						<form method="POST" action="?/syncStrava" use:enhance>
							<Button variant="outline" size="sm" type="submit">Sync</Button>
						</form>
					</div>
				{:else}
					<Button variant="outline" size="sm" href="/settings/integrations/strava/connect">
						Connect
					</Button>
				{/if}
			</div>
		</Card.Content>
	</Card.Root>
</div>
