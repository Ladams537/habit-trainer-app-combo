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

	let selectedExercises: Exercise[] = $state(
		data.template.exercises
			.sort((a: any, b: any) => a.sort_order - b.sort_order)
			.map((te: any) => {
				const ex = data.exercises.find((e: Exercise) => e.id === te.exercise_id);
				return ex || { id: te.exercise_id, user_id: null, name: te.exercise_name || 'Unknown', category: '', muscle_groups: [] as string[], equipment: null, is_custom: false, created_at: '' } satisfies Exercise;
			})
	);

	function addExercise(exercise: Exercise) {
		selectedExercises = [...selectedExercises, exercise];
		showPicker = false;
	}

	function removeExercise(index: number) {
		selectedExercises = selectedExercises.filter((_, i) => i !== index);
	}

	function moveUp(index: number) {
		if (index === 0) return;
		const arr = [...selectedExercises];
		[arr[index], arr[index - 1]] = [arr[index - 1], arr[index]];
		selectedExercises = arr;
	}

	function moveDown(index: number) {
		if (index >= selectedExercises.length - 1) return;
		const arr = [...selectedExercises];
		[arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
		selectedExercises = arr;
	}

	const exercisesJson = $derived(
		JSON.stringify(
			selectedExercises.map((e, i) => ({
				exercise_id: e.id,
				sort_order: i,
				target_sets: 3,
				target_reps: 10
			}))
		)
	);
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/programs/templates" variant="ghost" size="sm">
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
			<Input id="description" name="description" bind:value={description} placeholder="e.g. Chest, shoulders, triceps" />
		</div>

		<input type="hidden" name="exercises" value={exercisesJson} />

		<div class="space-y-3">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-semibold">Exercises</h2>
				<Button type="button" variant="outline" size="sm" onclick={() => (showPicker = !showPicker)}>
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
				<div class="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
					No exercises added. Click "Add Exercise" to build your template.
				</div>
			{:else}
				<div class="space-y-2">
					{#each selectedExercises as exercise, i}
						<div class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
							<span class="text-xs font-medium text-muted-foreground w-6">{i + 1}</span>
							<div class="flex-1 min-w-0">
								<span class="font-medium">{exercise.name}</span>
								<span class="ml-2 text-xs text-muted-foreground">{exercise.category}</span>
							</div>
							<div class="flex items-center gap-1">
								<button type="button" class="rounded p-1 text-muted-foreground hover:bg-accent" onclick={() => moveUp(i)} disabled={i === 0}>
									<ChevronUp class="h-4 w-4" />
								</button>
								<button type="button" class="rounded p-1 text-muted-foreground hover:bg-accent" onclick={() => moveDown(i)} disabled={i === selectedExercises.length - 1}>
									<ChevronDown class="h-4 w-4" />
								</button>
								<button type="button" class="rounded p-1 text-destructive hover:bg-accent" onclick={() => removeExercise(i)}>
									<Trash2 class="h-4 w-4" />
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<Button type="submit" class="w-full" disabled={!name}>Save Changes</Button>
	</form>

	<form method="POST" action="?/delete" use:enhance>
		<Button type="submit" variant="destructive" class="w-full">
			<Trash2 class="mr-1 h-4 w-4" />
			Delete Template
		</Button>
	</form>
</div>
