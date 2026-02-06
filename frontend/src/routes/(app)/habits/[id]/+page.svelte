<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import StreakDisplay from '$lib/components/habits/StreakDisplay.svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Flame from '@lucide/svelte/icons/flame';
	import Trophy from '@lucide/svelte/icons/trophy';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	let { data } = $props();

	const strengthPercent = $derived(Math.round(data.streak.strength * 100));
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/habits" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div class="flex-1">
			<div class="flex items-center gap-2">
				<span class="h-3 w-3 rounded-full" style="background-color: {data.habit.color}"></span>
				<h1 class="text-2xl font-bold">{data.habit.name}</h1>
			</div>
			<p class="text-sm text-muted-foreground capitalize">
				{data.habit.habit_type} &middot; {data.habit.frequency}
			</p>
		</div>
	</div>

	<!-- Stats cards -->
	<div class="grid grid-cols-3 gap-3">
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<Flame class="mb-1 h-5 w-5 text-orange-500" />
				<span class="text-2xl font-bold">{data.streak.current_streak}</span>
				<span class="text-xs text-muted-foreground">Current</span>
			</Card.Content>
		</Card.Root>
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<Trophy class="mb-1 h-5 w-5 text-yellow-500" />
				<span class="text-2xl font-bold">{data.streak.longest_streak}</span>
				<span class="text-xs text-muted-foreground">Best</span>
			</Card.Content>
		</Card.Root>
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<TrendingUp class="mb-1 h-5 w-5" style="color: var(--color-habits)" />
				<span class="text-2xl font-bold">{strengthPercent}%</span>
				<span class="text-xs text-muted-foreground">Strength</span>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Completion history -->
	<Card.Root>
		<Card.Header>
			<Card.Title>Recent completions</Card.Title>
		</Card.Header>
		<Card.Content>
			{#if data.streak.completion_dates.length === 0}
				<p class="text-sm text-muted-foreground">No completions yet.</p>
			{:else}
				<div class="flex flex-wrap gap-1.5">
					{#each data.streak.completion_dates.slice(-30) as d}
						<div
							class="h-6 w-6 rounded"
							style="background-color: {data.habit.color}"
							title={d}
						></div>
					{/each}
				</div>
				<p class="mt-2 text-xs text-muted-foreground">
					{data.streak.completion_dates.length} total completions
				</p>
			{/if}
		</Card.Content>
	</Card.Root>

	<!-- Delete -->
	<Card.Root class="border-destructive/50">
		<Card.Content class="flex items-center justify-between py-4">
			<div>
				<p class="font-medium">Archive habit</p>
				<p class="text-sm text-muted-foreground">Hides from daily view, keeps history</p>
			</div>
			<form method="POST" action="?/delete" use:enhance>
				<Button type="submit" variant="destructive" size="sm">
					<Trash2 class="mr-1 h-4 w-4" />
					Archive
				</Button>
			</form>
		</Card.Content>
	</Card.Root>
</div>
