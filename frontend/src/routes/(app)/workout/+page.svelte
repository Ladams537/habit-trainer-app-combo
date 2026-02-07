<script lang="ts">
	import { enhance } from '$app/forms';
	import { onMount } from 'svelte';
	import type { Exercise } from '$lib/api/fitness';
	import SetRow from '$lib/components/fitness/SetRow.svelte';
	import RestTimer from '$lib/components/fitness/RestTimer.svelte';
	import ExercisePicker from '$lib/components/fitness/ExercisePicker.svelte';
	import { Button } from '$lib/components/ui/button';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Plus from '@lucide/svelte/icons/plus';
	import Flag from '@lucide/svelte/icons/flag';
	import Timer from '@lucide/svelte/icons/timer';
	import MessageSquare from '@lucide/svelte/icons/message-square';

	let { data } = $props();

	// --- Elapsed timer ---
	const startedAt = new Date(data.session.started_at).getTime();
	let elapsed = $state(Math.floor((Date.now() - startedAt) / 1000));

	onMount(() => {
		const interval = setInterval(() => {
			elapsed = Math.floor((Date.now() - startedAt) / 1000);
		}, 1000);
		return () => clearInterval(interval);
	});

	const elapsedDisplay = $derived(() => {
		const h = Math.floor(elapsed / 3600);
		const m = Math.floor((elapsed % 3600) / 60);
		const s = elapsed % 60;
		if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
		return `${m}:${s.toString().padStart(2, '0')}`;
	});

	// --- Workout exercises ---
	interface WorkoutExercise {
		exercise: Exercise;
		sets: {
			id: string | null;
			set_number: number;
			weight_kg: number;
			reps: number;
			completed: boolean;
		}[];
		restSeconds: number;
	}

	function buildWorkoutExercises(): WorkoutExercise[] {
		const exercises: WorkoutExercise[] = [];
		const exerciseMap = new Map<string, WorkoutExercise>();

		for (const group of data.session.exercise_groups) {
			const we: WorkoutExercise = {
				exercise: group.exercise,
				sets: group.sets.map((s) => ({
					id: s.id,
					set_number: s.set_number,
					weight_kg: s.weight_kg,
					reps: s.reps,
					completed: s.completed
				})),
				restSeconds: 120
			};
			exercises.push(we);
			exerciseMap.set(group.exercise.id, we);
		}

		for (const templateExId of data.templateExercises) {
			if (!exerciseMap.has(templateExId)) {
				const exercise = data.exercises.find((e) => e.id === templateExId);
				if (exercise) {
					exercises.push({ exercise, sets: [], restSeconds: 120 });
				}
			}
		}

		return exercises;
	}

	let workoutExercises = $state(buildWorkoutExercises());
	let currentIndex = $state(0);
	let showRestTimer = $state(false);
	let showExercisePicker = $state(false);
	let showFinishPanel = $state(false);
	let workoutNotes = $state('');

	const currentExercise = $derived(workoutExercises[currentIndex]);
	const totalExercises = $derived(workoutExercises.length);

	const completedSetsCount = $derived(
		workoutExercises.reduce((sum, we) => sum + we.sets.filter((s) => s.completed).length, 0)
	);

	function getPrevious(exerciseId: string, setNum: number) {
		const prev = data.previousPerformance[exerciseId];
		if (!prev) return { weight: null, reps: null };
		const match = prev.find((s) => s.set_number === setNum);
		return match ? { weight: match.weight_kg, reps: match.reps } : { weight: null, reps: null };
	}

	function getDefaultWeight(exerciseId: string) {
		const prev = data.previousPerformance[exerciseId];
		if (prev && prev.length > 0) return prev[0].weight_kg;
		return 0;
	}

	function getDefaultReps(exerciseId: string) {
		const prev = data.previousPerformance[exerciseId];
		if (prev && prev.length > 0) return prev[0].reps;
		return 10;
	}

	function getTargetSets() {
		if (!currentExercise) return 3;
		const loggedCount = currentExercise.sets.length;
		return Math.max(loggedCount + 1, 3);
	}

	function onSetComplete() {
		showRestTimer = true;
	}

	function addExercise(exercise: Exercise) {
		workoutExercises.push({ exercise, sets: [], restSeconds: 120 });
		showExercisePicker = false;
		currentIndex = workoutExercises.length - 1;
	}

	function nextExercise() {
		if (currentIndex < totalExercises - 1) currentIndex++;
	}

	function prevExercise() {
		if (currentIndex > 0) currentIndex--;
	}
</script>

{#if showRestTimer}
	<RestTimer
		duration={currentExercise?.restSeconds ?? 120}
		onclose={() => (showRestTimer = false)}
	/>
{/if}

<div class="space-y-4">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div class="min-w-0 flex-1">
			<h1 class="truncate text-lg font-bold">
				{data.session.template_name || 'Workout'}
			</h1>
			<div class="flex items-center gap-2 text-xs text-muted-foreground">
				<Timer class="h-3.5 w-3.5" />
				<span class="tabular-nums">{elapsedDisplay()}</span>
				<span>·</span>
				<span>{completedSetsCount} set{completedSetsCount !== 1 ? 's' : ''}</span>
			</div>
		</div>
		<Button
			variant="default"
			size="sm"
			onclick={() => (showFinishPanel = !showFinishPanel)}
		>
			<Flag class="mr-1 h-4 w-4" />
			Finish
		</Button>
	</div>

	<!-- Finish panel with notes -->
	{#if showFinishPanel}
		<div class="rounded-xl border border-border bg-card p-4 space-y-3">
			<div class="flex items-center gap-2 text-sm font-medium">
				<MessageSquare class="h-4 w-4 text-muted-foreground" />
				Workout Notes
			</div>
			<textarea
				bind:value={workoutNotes}
				placeholder="How did the workout feel? Any PRs, tweaks, or things to remember..."
				rows={3}
				class="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none"
			></textarea>
			<div class="flex gap-2">
				<form method="POST" action="?/completeWorkout" use:enhance class="flex-1">
					<input type="hidden" name="sessionId" value={data.session.id} />
					<input type="hidden" name="notes" value={workoutNotes} />
					<Button type="submit" class="w-full">
						Finish Workout
					</Button>
				</form>
				<Button variant="outline" onclick={() => (showFinishPanel = false)}>
					Cancel
				</Button>
			</div>
		</div>
	{/if}

	{#if showExercisePicker}
		<div class="rounded-xl border border-border bg-card p-4">
			<ExercisePicker
				exercises={data.exercises}
				onselect={addExercise}
				onclose={() => (showExercisePicker = false)}
			/>
		</div>
	{:else if workoutExercises.length === 0}
		<div
			class="rounded-xl border border-border bg-card p-8 text-center text-muted-foreground"
		>
			<p class="mb-3">No exercises yet. Add one to get started.</p>
			<Button variant="outline" onclick={() => (showExercisePicker = true)}>
				<Plus class="mr-1 h-4 w-4" />
				Add Exercise
			</Button>
		</div>
	{:else if currentExercise}
		<!-- Exercise navigation -->
		<div class="flex items-center justify-between rounded-xl bg-muted px-2 py-2">
			<button
				type="button"
				class="flex h-11 w-11 items-center justify-center rounded-lg transition-colors hover:bg-accent active:scale-95 disabled:opacity-30"
				onclick={prevExercise}
				disabled={currentIndex === 0}
			>
				<ChevronLeft class="h-5 w-5" />
			</button>
			<div class="min-w-0 flex-1 text-center">
				<div class="truncate font-semibold">{currentExercise.exercise.name}</div>
				<div class="text-xs text-muted-foreground">
					{currentIndex + 1} / {totalExercises}
					{#if currentExercise.exercise.muscle_groups.length > 0}
						· {currentExercise.exercise.muscle_groups.slice(0, 2).join(', ')}
					{/if}
				</div>
			</div>
			<button
				type="button"
				class="flex h-11 w-11 items-center justify-center rounded-lg transition-colors hover:bg-accent active:scale-95 disabled:opacity-30"
				onclick={nextExercise}
				disabled={currentIndex >= totalExercises - 1}
			>
				<ChevronRight class="h-5 w-5" />
			</button>
		</div>

		<!-- Set rows — keyed on exercise to force recreation when switching -->
		{#key currentExercise.exercise.id}
			<div class="space-y-2">
				{#each { length: getTargetSets() } as _, i}
					{@const existingSet = currentExercise.sets[i]}
					{@const prev = getPrevious(currentExercise.exercise.id, i + 1)}
					<SetRow
						setNumber={i + 1}
						weight={existingSet?.weight_kg ?? getDefaultWeight(currentExercise.exercise.id)}
						reps={existingSet?.reps ?? getDefaultReps(currentExercise.exercise.id)}
						previousWeight={prev.weight}
						previousReps={prev.reps}
						completed={existingSet?.completed ?? false}
						setId={existingSet?.id ?? null}
						sessionId={data.session.id}
						exerciseId={currentExercise.exercise.id}
						oncomplete={onSetComplete}
					/>
				{/each}
			</div>
		{/key}

		<!-- Bottom actions -->
		<div class="flex gap-2">
			<Button
				variant="outline"
				class="flex-1"
				onclick={() => {
					currentExercise.sets.push({
						id: null,
						set_number: currentExercise.sets.length + 1,
						weight_kg: getDefaultWeight(currentExercise.exercise.id),
						reps: getDefaultReps(currentExercise.exercise.id),
						completed: false
					});
				}}
			>
				<Plus class="mr-1 h-4 w-4" />
				Add Set
			</Button>
			<Button variant="ghost" onclick={() => (showExercisePicker = true)}>
				<Plus class="mr-1 h-4 w-4" />
				Exercise
			</Button>
		</div>
	{/if}
</div>
