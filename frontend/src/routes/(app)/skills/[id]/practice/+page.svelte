<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import PracticeTimer from '$lib/components/skills/PracticeTimer.svelte';
	import QualityRating from '$lib/components/skills/QualityRating.svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';

	let { data, form } = $props();

	let phase: 'timer' | 'review' = $state('timer');
	let durationMinutes = $state(0);
	let qualityRating = $state(0);
	let focusArea = $state('');
	let notes = $state('');

	// Due sub-skills listed first
	const dueSubSkills = $derived(
		data.schedule.schedule.filter((s) => s.is_due).map((s) => s.sub_skill)
	);

	function handleStop(seconds: number) {
		durationMinutes = Math.max(1, Math.round(seconds / 60));
		phase = 'review';
	}
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/skills/{data.skill.id}" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div>
			<h1 class="text-2xl font-bold">Practice</h1>
			<p class="text-sm text-muted-foreground">{data.skill.name}</p>
		</div>
	</div>

	{#if phase === 'timer'}
		<Card.Root>
			<Card.Content class="py-8">
				<!-- Focus area selector -->
				{#if data.skill.sub_skills.length > 0}
					<div class="mb-6 space-y-2">
						<Label>Focus area</Label>
						<select
							bind:value={focusArea}
							class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
						>
							<option value="">General practice (all sub-skills)</option>
							{#each data.skill.sub_skills as sub}
								<option value={sub}>
									{sub}{dueSubSkills.includes(sub) ? ' (due)' : ''}
								</option>
							{/each}
						</select>
					</div>
				{/if}

				<PracticeTimer onstop={handleStop} />
			</Card.Content>
		</Card.Root>
	{:else}
		<Card.Root>
			<Card.Content class="pt-6">
				<form method="POST" use:enhance class="space-y-4">
					{#if form?.error}
						<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
							{form.error}
						</div>
					{/if}

					<input type="hidden" name="duration_minutes" value={durationMinutes} />
					<input type="hidden" name="quality_rating" value={qualityRating} />
					<input type="hidden" name="focus_area" value={focusArea} />

					<div class="text-center">
						<p class="text-3xl font-bold">{durationMinutes} min</p>
						<p class="text-sm text-muted-foreground">Practice completed</p>
					</div>

					<div class="space-y-2">
						<Label>How did it go?</Label>
						<QualityRating bind:value={qualityRating} />
					</div>

					<div class="space-y-2">
						<Label for="notes">Notes (optional)</Label>
						<Input
							id="notes"
							name="notes"
							bind:value={notes}
							placeholder="What did you work on?"
						/>
					</div>

					<div class="flex gap-3 pt-2">
						<Button
							type="submit"
							class="flex-1 bg-purple-600 hover:bg-purple-700"
							disabled={qualityRating === 0}
						>
							Save Practice
						</Button>
						<Button href="/skills/{data.skill.id}" variant="outline">Discard</Button>
					</div>
				</form>
			</Card.Content>
		</Card.Root>
	{/if}
</div>
