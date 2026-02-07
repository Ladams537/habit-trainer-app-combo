<script lang="ts">
	import { enhance } from '$app/forms';
	import Check from '@lucide/svelte/icons/check';
	import Plus from '@lucide/svelte/icons/plus';
	import Minus from '@lucide/svelte/icons/minus';
	import StreakDisplay from './StreakDisplay.svelte';

	let {
		habit
	}: {
		habit: {
			id: string;
			name: string;
			habit_type: string;
			target_value: number;
			unit: string | null;
			color: string;
			completed_today: boolean;
			today_value: number;
			current_streak: number;
			strength: number;
		};
	} = $props();

	let optimisticCompleted = $state(habit.completed_today);
	let optimisticValue = $state(habit.today_value);
	let durationInput = $state('');

	$effect(() => {
		optimisticCompleted = habit.completed_today;
		optimisticValue = habit.today_value;
	});

	const isComplete = $derived(
		habit.habit_type === 'boolean'
			? optimisticCompleted
			: optimisticValue >= habit.target_value
	);
</script>

<div
	class="flex w-full items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-all"
>
	<!-- Completion indicator -->
	{#if habit.habit_type === 'boolean'}
		<form
			method="POST"
			action="/today?/toggleHabit"
			use:enhance={() => {
				optimisticCompleted = !optimisticCompleted;
				return async ({ update }) => {
					await update();
				};
			}}
		>
			<input type="hidden" name="habitId" value={habit.id} />
			<input type="hidden" name="completed" value={habit.completed_today ? 'false' : 'true'} />
			<button
				type="submit"
				class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition-all hover:scale-110 active:scale-95"
				style="border-color: {habit.color}; {optimisticCompleted
					? `background-color: ${habit.color}`
					: ''}"
			>
				{#if optimisticCompleted}
					<Check class="h-4 w-4 text-white" />
				{/if}
			</button>
		</form>
	{:else}
		<div
			class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition-all"
			style="border-color: {habit.color}; {isComplete
				? `background-color: ${habit.color}`
				: ''}"
		>
			{#if isComplete}
				<Check class="h-4 w-4 text-white" />
			{/if}
		</div>
	{/if}

	<!-- Habit info -->
	<div class="flex-1 min-w-0">
		<div class="flex items-center gap-2">
			<span
				class="font-medium truncate {isComplete
					? 'text-muted-foreground line-through'
					: 'text-foreground'}"
			>
				{habit.name}
			</span>
		</div>
		<StreakDisplay streak={habit.current_streak} strength={habit.strength} />
	</div>

	<!-- Type-specific controls -->
	{#if habit.habit_type === 'numeric'}
		<div class="flex items-center gap-2">
			<span class="text-sm text-muted-foreground tabular-nums">
				{optimisticValue}/{habit.target_value}
				{habit.unit || ''}
			</span>
			<form
				method="POST"
				action="/today?/toggleHabit"
				class="inline"
				use:enhance={() => {
					optimisticValue = Math.max(0, optimisticValue - 1);
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<input type="hidden" name="habitId" value={habit.id} />
				<input type="hidden" name="completed" value="false" />
				<button
					type="submit"
					class="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground active:scale-95 disabled:opacity-30"
					disabled={optimisticValue <= 0}
				>
					<Minus class="h-3.5 w-3.5" />
				</button>
			</form>
			<form
				method="POST"
				action="/today?/logHabit"
				class="inline"
				use:enhance={() => {
					optimisticValue = optimisticValue + 1;
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<input type="hidden" name="habitId" value={habit.id} />
				<input type="hidden" name="value" value="1" />
				<button
					type="submit"
					class="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground active:scale-95"
				>
					<Plus class="h-3.5 w-3.5" />
				</button>
			</form>
		</div>
	{:else if habit.habit_type === 'duration'}
		<div class="flex items-center gap-2">
			<span class="text-sm text-muted-foreground tabular-nums">
				{optimisticValue}/{habit.target_value}
				{habit.unit || 'min'}
			</span>
			<form
				method="POST"
				action="/today?/logHabit"
				class="flex items-center gap-1.5"
				use:enhance={() => {
					const val = parseFloat(durationInput);
					if (!isNaN(val) && val > 0) {
						optimisticValue = optimisticValue + val;
						durationInput = '';
					}
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<input type="hidden" name="habitId" value={habit.id} />
				<input
					type="number"
					name="value"
					bind:value={durationInput}
					placeholder="0"
					min="1"
					step="1"
					class="h-7 w-14 rounded-md border border-border bg-background px-2 text-sm tabular-nums text-center focus:outline-none focus:ring-1 focus:ring-ring"
				/>
				<button
					type="submit"
					disabled={!durationInput || parseFloat(durationInput) <= 0}
					class="h-7 rounded-md border border-border px-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground active:scale-95 disabled:opacity-30"
				>
					Log
				</button>
			</form>
		</div>
	{/if}
</div>
