<script lang="ts">
	import HabitCard from './HabitCard.svelte';
	import type { HabitToday } from '$lib/api/habits';

	let { habits }: { habits: HabitToday[] } = $props();

	const completedCount = $derived(habits.filter((h) => h.completed_today).length);
</script>

<div class="space-y-3">
	<div class="flex items-center justify-between">
		<h2 class="flex items-center gap-2 text-lg font-semibold">
			<span
				class="inline-block h-3 w-3 rounded-full"
				style="background-color: var(--color-habits)"
			></span>
			Habits
		</h2>
		<span class="text-sm text-muted-foreground">
			{completedCount}/{habits.length} done
		</span>
	</div>

	{#if habits.length === 0}
		<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
			No habits due today.
			<a href="/habits/new" class="text-primary underline-offset-4 hover:underline">Create one</a>
		</div>
	{:else}
		<div class="space-y-2">
			{#each habits as habit (habit.id)}
				<HabitCard {habit} />
			{/each}
		</div>
	{/if}
</div>
