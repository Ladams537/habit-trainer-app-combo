<script lang="ts">
	import { enhance } from '$app/forms';
	import type { Exercise } from '$lib/api/fitness';
	import ExercisePicker from '$lib/components/fitness/ExercisePicker.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Plus from '@lucide/svelte/icons/plus';

	let { data } = $props();

	let name = $state(data.template.name);
	let description = $state(data.template.description || '');
	let showPicker = $state(false);

	interface TemplateExEntry {
		exercise: Exercise;
		target_sets: number;
		target_reps: number;
		target_weight_kg: string;
		rest_seconds: number;
	}

	let selectedExercises: TemplateExEntry[] = $state(
		data.template.exercises.map((te) => ({
			exercise: te.exercise,
			target_sets: te.target_sets,
			target_reps: te.target_reps,
			target_weight_kg: te.target_weight_kg?.toString() || '',
			rest_seconds: te.rest_seconds
		}))
	);

	function addExercise(exercise: Exercise) {
		selectedExercises.push({
			exercise,
			target_sets: 3,
			target_reps: 10,
			target_weight_kg: '',
			rest_seconds: 120
		});
		showPicker = false;
	}

	function removeExercise(index: number) {
		selectedExercises.splice(index, 1);
	}

	function moveUp(index: number) {
		if (index === 0) return;
		const temp = selectedExercises[index];
		selectedExercises[index] = selectedExercises[index - 1];
		selectedExercises[index - 1] = temp;
	}

	function moveDown(index: number) {
		if (index >= selectedExercises.length - 1) return;
		const temp = selectedExercises[index];
		selectedExercises[index] = selectedExercises[index + 1];
		selectedExercises[index + 1] = temp;
	}

	const exercisesJson = $derived(
		JSON.stringify(
			selectedExercises.map((e, i) => ({
				exercise_id: e.exercise.id,
				sort_order: i,
				target_sets: e.target_sets,
				target_reps: e.target_reps,
				target_weight_kg: e.target_weight_kg ? parseFloat(e.target_weight_kg) : undefined,
				rest_seconds: e.rest_seconds
			}))
		)
	);
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/plan" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<h1 class="text-2xl font-bold">Edit Template</h1>
	</div>

	<form method="POST" action="?/update" use:enhance class="space-y-6">
		<div class="space-y-2">
			<Label for="name">Template Name</Label>
			<Input id="name" name="name" bind:value={name} placeholder="e.g. Push Day" required />
		</div>

		<div class="space-y-2">
			<Label for="description">Description (optional)</Label>
			<Input
				id="description"
				name="description"
				bind:value={description}
				placeholder="e.g. Chest, shoulders, triceps"
			/>
		</div>

		<input type="hidden" name="exercises" value={exercisesJson} />

		<div class="space-y-3">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-semibold">Exercises</h2>
				<Button
					type="button"
					variant="outline"
					size="sm"
					onclick={() => (showPicker = !showPicker)}
				>
					<Plus class="mr-1 h-4 w-4" />
					Add Exercise
				</Button>
			</div>

			{#if showPicker}
				<div class="rounded-lg border border-border bg-card p-4">
					<ExercisePicker
						exercises={data.exercises}
						onselect={addExercise}
						onclose={() => (showPicker = false)}
					/>
				</div>
			{/if}

			{#if selectedExercises.length === 0}
				<div
					class="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground"
				>
					No exercises added.
				</div>
			{:else}
				<div class="space-y-3">
					{#each selectedExercises as entry, i}
						<div class="rounded-lg border border-border bg-card p-4">
							<div class="mb-3 flex items-center justify-between">
								<div>
									<span class="font-medium">{entry.exercise.name}</span>
									<span class="ml-2 text-xs text-muted-foreground">
										{entry.exercise.category}
									</span>
								</div>
								<div class="flex items-center gap-1">
									<button
										type="button"
										class="rounded p-1 text-muted-foreground hover:bg-accent"
										onclick={() => moveUp(i)}
										disabled={i === 0}
									>
										<ChevronUp class="h-4 w-4" />
									</button>
									<button
										type="button"
										class="rounded p-1 text-muted-foreground hover:bg-accent"
										onclick={() => moveDown(i)}
										disabled={i === selectedExercises.length - 1}
									>
										<ChevronDown class="h-4 w-4" />
									</button>
									<button
										type="button"
										class="rounded p-1 text-destructive hover:bg-accent"
										onclick={() => removeExercise(i)}
									>
										<Trash2 class="h-4 w-4" />
									</button>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								<div>
									<label class="text-xs text-muted-foreground">Sets</label>
									<Input
										type="number"
										bind:value={entry.target_sets}
										min="1"
										max="20"
										class="mt-1"
									/>
								</div>
								<div>
									<label class="text-xs text-muted-foreground">Reps</label>
									<Input
										type="number"
										bind:value={entry.target_reps}
										min="1"
										max="100"
										class="mt-1"
									/>
								</div>
								<div>
									<label class="text-xs text-muted-foreground">Weight (kg)</label>
									<Input
										type="number"
										bind:value={entry.target_weight_kg}
										min="0"
										step="2.5"
										placeholder="—"
										class="mt-1"
									/>
								</div>
								<div>
									<label class="text-xs text-muted-foreground">Rest (s)</label>
									<Input
										type="number"
										bind:value={entry.rest_seconds}
										min="0"
										step="15"
										class="mt-1"
									/>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<div class="flex gap-3">
			<Button type="submit" class="flex-1" disabled={!name}>Save Changes</Button>
		</div>
	</form>

	<form method="POST" action="?/delete" use:enhance>
		<Button type="submit" variant="destructive" class="w-full">
			<Trash2 class="mr-1 h-4 w-4" />
			Delete Template
		</Button>
	</form>
</div>
