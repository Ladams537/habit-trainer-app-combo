<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	let { form } = $props();

	let currentLevel = $state('beginner');
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold">New skill</h1>

	<Card.Root>
		<Card.Content class="pt-6">
			<form method="POST" use:enhance class="space-y-4">
				{#if form?.error}
					<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
						{form.error}
					</div>
				{/if}

				<div class="space-y-2">
					<Label for="name">Name</Label>
					<Input id="name" name="name" required placeholder="e.g. Guitar, Drawing, Cooking" />
				</div>

				<div class="space-y-2">
					<Label for="category">Category</Label>
					<select
						id="category"
						name="category"
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
					>
						<option value="general">General</option>
						<option value="music">Music</option>
						<option value="language">Language</option>
						<option value="art">Art</option>
						<option value="coding">Coding</option>
						<option value="sport">Sport</option>
						<option value="cooking">Cooking</option>
					</select>
				</div>

				<div class="space-y-2">
					<Label for="sub_skills">Sub-skills</Label>
					<Input
						id="sub_skills"
						name="sub_skills"
						placeholder="e.g. Chords, Scales, Fingerpicking (comma-separated)"
					/>
					<p class="text-xs text-muted-foreground">
						Separate sub-skills with commas. Each gets its own spaced repetition schedule.
					</p>
				</div>

				<div class="space-y-2">
					<Label for="current_level">Level</Label>
					<select
						id="current_level"
						name="current_level"
						bind:value={currentLevel}
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
					>
						<option value="beginner">Beginner</option>
						<option value="intermediate">Intermediate</option>
						<option value="advanced">Advanced</option>
					</select>
				</div>

				<div class="flex gap-3 pt-2">
					<Button type="submit" class="flex-1">Create skill</Button>
					<Button href="/skills" variant="outline">Cancel</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>
</div>
