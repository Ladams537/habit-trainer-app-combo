<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import StreakDisplay from '$lib/components/habits/StreakDisplay.svelte';
	import Plus from '@lucide/svelte/icons/plus';

	let { data } = $props();
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Habits</h1>
		<Button href="/habits/new" size="sm">
			<Plus class="mr-1 h-4 w-4" />
			New habit
		</Button>
	</div>

	{#if data.habits.length === 0}
		<Card.Root>
			<Card.Content class="py-8 text-center text-muted-foreground">
				No habits yet. Create your first habit to start tracking.
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="space-y-2">
			{#each data.habits as habit (habit.id)}
				<a
					href="/habits/{habit.id}"
					class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent/50"
				>
					<span
						class="h-3 w-3 shrink-0 rounded-full"
						style="background-color: {habit.color}"
					></span>
					<div class="flex-1 min-w-0">
						<p class="font-medium truncate">{habit.name}</p>
						<p class="text-xs text-muted-foreground capitalize">{habit.habit_type} &middot; {habit.frequency}</p>
					</div>
					<StreakDisplay streak={habit.current_streak} strength={habit.strength} />
				</a>
			{/each}
		</div>
	{/if}
</div>
