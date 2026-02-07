<script lang="ts">
	import { enhance } from '$app/forms';
	import Check from '@lucide/svelte/icons/check';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	let {
		setNumber,
		weight,
		reps,
		previousWeight,
		previousReps,
		completed,
		setId,
		sessionId,
		exerciseId,
		oncomplete
	}: {
		setNumber: number;
		weight: number;
		reps: number;
		previousWeight: number | null;
		previousReps: number | null;
		completed: boolean;
		setId: string | null;
		sessionId: string;
		exerciseId: string;
		oncomplete?: () => void;
	} = $props();

	let currentWeight = $state(weight);
	let currentReps = $state(reps);
	let isCompleted = $state(completed);

	function adjustWeight(delta: number) {
		currentWeight = Math.max(0, +(currentWeight + delta).toFixed(1));
	}

	function adjustReps(delta: number) {
		currentReps = Math.max(0, currentReps + delta);
	}
</script>

<div
	class="rounded-xl border px-3 py-2.5 {isCompleted
		? 'border-primary/20 bg-primary/5'
		: 'border-border bg-card'}"
>
	<!-- Top row: set label + previous -->
	<div class="mb-2 flex items-center justify-between">
		<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
			Set {setNumber}
		</span>
		<span class="text-xs text-muted-foreground">
			{#if previousWeight !== null && previousReps !== null}
				prev: {previousWeight} kg × {previousReps}
			{:else}
				—
			{/if}
		</span>
	</div>

	<!-- Bottom row: weight + reps + action -->
	<div class="flex items-center gap-2">
		<!-- Weight stepper -->
		<div class="flex flex-1 flex-col items-center gap-1">
			<span class="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">kg</span>
			<div class="flex items-center">
				<button
					type="button"
					class="flex h-11 w-11 items-center justify-center rounded-l-lg border border-border text-base font-bold active:bg-accent active:scale-95"
					onclick={() => adjustWeight(-2.5)}
				>
					−
				</button>
				<input
					type="number"
					inputmode="decimal"
					step="0.5"
					min="0"
					bind:value={currentWeight}
					onfocus={(e) => e.currentTarget.select()}
					class="h-11 w-[3.5rem] border-y border-border bg-background text-center text-sm font-semibold tabular-nums focus:outline-none focus:ring-1 focus:ring-ring focus:z-10"
				/>
				<button
					type="button"
					class="flex h-11 w-11 items-center justify-center rounded-r-lg border border-border text-base font-bold active:bg-accent active:scale-95"
					onclick={() => adjustWeight(2.5)}
				>
					+
				</button>
			</div>
		</div>

		<!-- Reps stepper -->
		<div class="flex flex-1 flex-col items-center gap-1">
			<span class="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">reps</span>
			<div class="flex items-center">
				<button
					type="button"
					class="flex h-11 w-11 items-center justify-center rounded-l-lg border border-border text-base font-bold active:bg-accent active:scale-95"
					onclick={() => adjustReps(-1)}
				>
					−
				</button>
				<input
					type="number"
					inputmode="numeric"
					step="1"
					min="0"
					bind:value={currentReps}
					onfocus={(e) => e.currentTarget.select()}
					class="h-11 w-[2.5rem] border-y border-border bg-background text-center text-sm font-semibold tabular-nums focus:outline-none focus:ring-1 focus:ring-ring focus:z-10"
				/>
				<button
					type="button"
					class="flex h-11 w-11 items-center justify-center rounded-r-lg border border-border text-base font-bold active:bg-accent active:scale-95"
					onclick={() => adjustReps(1)}
				>
					+
				</button>
			</div>
		</div>

		<!-- Complete / undo -->
		<div class="flex flex-col items-center gap-1">
			<span class="text-[10px] font-medium uppercase tracking-wider text-transparent">ok</span>
			{#if !isCompleted}
				<form
					method="POST"
					action="/workout?/logSet"
					use:enhance={() => {
						isCompleted = true;
						oncomplete?.();
						return async ({ update }) => {
							await update();
						};
					}}
				>
					<input type="hidden" name="sessionId" value={sessionId} />
					<input type="hidden" name="exerciseId" value={exerciseId} />
					<input type="hidden" name="setNumber" value={setNumber} />
					<input type="hidden" name="weight" value={currentWeight} />
					<input type="hidden" name="reps" value={currentReps} />
					<button
						type="submit"
						class="flex h-11 w-11 items-center justify-center rounded-lg border-2 border-primary text-primary transition-all hover:bg-primary hover:text-primary-foreground active:scale-90"
					>
						<Check class="h-5 w-5" />
					</button>
				</form>
			{:else if setId}
				<form
					method="POST"
					action="/workout?/deleteSet"
					use:enhance={() => {
						isCompleted = false;
						return async ({ update }) => {
							await update();
						};
					}}
				>
					<input type="hidden" name="sessionId" value={sessionId} />
					<input type="hidden" name="setId" value={setId} />
					<button
						type="submit"
						class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary transition-all active:scale-90"
					>
						<Trash2 class="h-4 w-4" />
					</button>
				</form>
			{:else}
				<div
					class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary"
				>
					<Check class="h-5 w-5" />
				</div>
			{/if}
		</div>
	</div>
</div>
