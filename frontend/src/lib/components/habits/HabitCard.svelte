<script lang="ts">
	import { enhance } from '$app/forms';
	import Check from '@lucide/svelte/icons/check';
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

	$effect(() => {
		optimisticCompleted = habit.completed_today;
	});
</script>

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
		class="flex w-full items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 text-left transition-all hover:bg-accent/50 active:scale-[0.98]"
	>
		<!-- Completion indicator -->
		<div
			class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition-all"
			style="border-color: {habit.color}; {optimisticCompleted
				? `background-color: ${habit.color}`
				: ''}"
		>
			{#if optimisticCompleted}
				<Check class="h-4 w-4 text-white" />
			{/if}
		</div>

		<!-- Habit info -->
		<div class="flex-1 min-w-0">
			<div class="flex items-center gap-2">
				<span
					class="font-medium truncate {optimisticCompleted
						? 'text-muted-foreground line-through'
						: 'text-foreground'}"
				>
					{habit.name}
				</span>
			</div>
			<StreakDisplay streak={habit.current_streak} strength={habit.strength} />
		</div>

		<!-- Value for numeric/duration habits -->
		{#if habit.habit_type !== 'boolean'}
			<span class="text-sm text-muted-foreground">
				{habit.today_value}/{habit.target_value}
				{habit.unit || ''}
			</span>
		{/if}
	</button>
</form>
