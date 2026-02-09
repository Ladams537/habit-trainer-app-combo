<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import WeekPrescriptionEditor from '$lib/components/fitness/WeekPrescriptionEditor.svelte';
	import ProgressionPicker from '$lib/components/fitness/ProgressionPicker.svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Play from '@lucide/svelte/icons/play';
	import CheckCircle from '@lucide/svelte/icons/check-circle';
	import type { ProgramDayPrescription } from '$lib/api/programs';

	let { data, form } = $props();

	let prescriptions = $state<ProgramDayPrescription[]>(data.week.prescriptions);
	let recoveryRating = $state(3);
	let weekNotes = $state('');
	let showCompleteForm = $state(false);
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/programs/{data.program.id}" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div class="flex-1">
			<h1 class="text-xl font-bold">{data.program.name} - Week {data.weekNum}</h1>
			<p class="text-sm text-muted-foreground capitalize">{data.week.status}
				{#if data.week.progression_source}
					· {data.week.progression_source}
				{/if}
			</p>
		</div>
	</div>

	{#if form?.error}
		<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
			{form.error}
		</div>
	{/if}

	<!-- Prescription Editor -->
	{#if data.week.status === 'active' || data.week.status === 'pending'}
		<WeekPrescriptionEditor bind:prescriptions />

		<div class="flex gap-3">
			<form method="POST" action="?/savePrescriptions" use:enhance class="flex-1">
				<input type="hidden" name="prescriptions" value={JSON.stringify(prescriptions)} />
				<Button type="submit" class="w-full">Save Prescriptions</Button>
			</form>
		</div>

		<!-- Start workout buttons -->
		<Card.Root>
			<Card.Header>
				<Card.Title class="text-base">Start Workout</Card.Title>
			</Card.Header>
			<Card.Content class="space-y-2">
				{#each prescriptions as day, i}
					<form method="POST" action="?/startSession" use:enhance>
						<input type="hidden" name="day_index" value={i} />
						<Button type="submit" variant="outline" class="w-full justify-start">
							<Play class="mr-2 h-4 w-4" />
							{day.day_label}
						</Button>
					</form>
				{/each}
			</Card.Content>
		</Card.Root>

		<!-- Complete Week -->
		{#if !showCompleteForm}
			<Button variant="outline" onclick={() => (showCompleteForm = true)} class="w-full">
				<CheckCircle class="mr-2 h-4 w-4" />
				Complete Week
			</Button>
		{:else}
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-base">Complete Week {data.weekNum}</Card.Title>
				</Card.Header>
				<Card.Content>
					<form method="POST" action="?/completeWeek" use:enhance class="space-y-4">
						<div class="space-y-2">
							<Label>Recovery Rating (1-5)</Label>
							<div class="flex gap-2">
								{#each [1, 2, 3, 4, 5] as rating}
									<button
										type="button"
										onclick={() => (recoveryRating = rating)}
										class="flex h-10 w-10 items-center justify-center rounded-lg border text-sm font-medium transition-colors
											{recoveryRating === rating ? 'border-primary bg-primary text-primary-foreground' : 'border-border hover:bg-accent'}"
									>
										{rating}
									</button>
								{/each}
							</div>
							<p class="text-xs text-muted-foreground">1 = very fatigued, 5 = fully recovered</p>
						</div>
						<input type="hidden" name="recovery_rating" value={recoveryRating} />

						<div class="space-y-2">
							<Label for="notes">Notes (optional)</Label>
							<Input id="notes" name="notes" bind:value={weekNotes} placeholder="How did this week go?" />
						</div>

						<div class="flex gap-3">
							<Button type="submit" class="flex-1">Complete Week</Button>
							<Button type="button" variant="outline" onclick={() => (showCompleteForm = false)}>Cancel</Button>
						</div>
					</form>
				</Card.Content>
			</Card.Root>
		{/if}
	{/if}

	<!-- Completed week: show progression options -->
	{#if data.week.status === 'completed'}
		<Card.Root>
			<Card.Content class="py-4">
				<div class="flex items-center gap-2">
					<CheckCircle class="h-5 w-5 text-green-500" />
					<span class="font-medium">Week completed</span>
				</div>
				{#if data.week.recovery_rating}
					<p class="text-sm text-muted-foreground mt-1">Recovery: {data.week.recovery_rating}/5</p>
				{/if}
				{#if data.week.notes}
					<p class="text-sm text-muted-foreground mt-1">{data.week.notes}</p>
				{/if}
			</Card.Content>
		</Card.Root>

		<!-- Read-only prescriptions -->
		<WeekPrescriptionEditor prescriptions={data.week.prescriptions} readonly />

		{#if data.progressionOptions}
			<h2 class="text-lg font-semibold">Generate Next Week</h2>
			<ProgressionPicker
				options={data.progressionOptions.options}
				currentPrescriptions={data.week.prescriptions}
				programId={data.program.id}
				weekNum={data.weekNum}
			/>
		{/if}
	{/if}
</div>
