<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Clock from '@lucide/svelte/icons/clock';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import Zap from '@lucide/svelte/icons/zap';
	import Smile from '@lucide/svelte/icons/smile';
	import type { ExerciseSetsGroup } from '$lib/api/fitness';

	let { data } = $props();

	const session = data.session;

	function formatDuration() {
		if (!session.completed_at) return 'In progress';
		const start = new Date(session.started_at).getTime();
		const end = new Date(session.completed_at).getTime();
		const mins = Math.round((end - start) / 60000);
		if (mins < 60) return `${mins} min`;
		return `${Math.floor(mins / 60)}h ${mins % 60}m`;
	}

	const totalVolume = $derived(
		session.exercise_groups.reduce(
			(sum, g) =>
				sum + g.sets.reduce((s, set) => s + (set.completed ? set.weight_kg * set.reps : 0), 0),
			0
		)
	);

	const totalSets = $derived(
		session.exercise_groups.reduce(
			(sum, g) => sum + g.sets.filter((s) => s.completed).length,
			0
		)
	);

	function getProgressionSuggestion(group: ExerciseSetsGroup): string | null {
		const workingSets = group.sets.filter((s) => s.completed && s.set_type === 'working');
		if (workingSets.length < 2) return null;

		const weights = workingSets.map((s) => s.weight_kg);
		const allSameWeight = weights.every((w) => w === weights[0]);
		if (!allSameWeight) return null;

		const weight = weights[0];

		if (weight === 0) {
			return 'All sets completed at bodyweight — try +1 rep per set next session';
		}

		const increment = weight >= 25 ? 2.5 : 1.0;
		const nextWeight = weight + increment;
		return `All sets completed at ${weight}kg — try ${nextWeight}kg next session`;
	}

	function renderRating(value: number, max: number = 5): { filled: number; empty: number } {
		return { filled: value, empty: max - value };
	}
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/calendar" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div>
			<h1 class="text-2xl font-bold">
				{session.template_name || 'Free-form Workout'}
			</h1>
			<div class="flex items-center gap-3 text-sm text-muted-foreground">
				<span>
					{new Date(session.started_at).toLocaleDateString('en-GB', {
						weekday: 'long',
						day: 'numeric',
						month: 'long',
						year: 'numeric'
					})}
				</span>
				{#if session.completed_at}
					<span class="flex items-center gap-1">
						<Clock class="h-3.5 w-3.5" />
						{formatDuration()}
					</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- Summary stats -->
	<div class="grid grid-cols-3 gap-3">
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="text-2xl font-bold tabular-nums">{session.exercise_groups.length}</div>
			<div class="text-xs text-muted-foreground">Exercises</div>
		</div>
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="text-2xl font-bold tabular-nums">{totalSets}</div>
			<div class="text-xs text-muted-foreground">Sets</div>
		</div>
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="text-2xl font-bold tabular-nums">{Math.round(totalVolume)}</div>
			<div class="text-xs text-muted-foreground">Volume (kg)</div>
		</div>
	</div>

	<!-- Session Rating -->
	{#if session.rating_energy || session.rating_mood}
		<div class="rounded-lg border border-border bg-card p-4 space-y-2">
			<h3 class="text-sm font-medium text-muted-foreground">Session Rating</h3>
			<div class="flex flex-col gap-2">
				{#if session.rating_energy}
					{@const rating = renderRating(session.rating_energy)}
					<div class="flex items-center gap-2">
						<Zap class="h-4 w-4 text-amber-500" />
						<span class="text-sm w-14">Energy</span>
						<div class="flex gap-0.5">
							{#each Array(rating.filled) as _}
								<span class="h-3 w-3 rounded-full bg-amber-500"></span>
							{/each}
							{#each Array(rating.empty) as _}
								<span class="h-3 w-3 rounded-full bg-muted"></span>
							{/each}
						</div>
						<span class="text-xs text-muted-foreground">{session.rating_energy}/5</span>
					</div>
				{/if}
				{#if session.rating_mood}
					{@const rating = renderRating(session.rating_mood)}
					<div class="flex items-center gap-2">
						<Smile class="h-4 w-4 text-blue-500" />
						<span class="text-sm w-14">Mood</span>
						<div class="flex gap-0.5">
							{#each Array(rating.filled) as _}
								<span class="h-3 w-3 rounded-full bg-blue-500"></span>
							{/each}
							{#each Array(rating.empty) as _}
								<span class="h-3 w-3 rounded-full bg-muted"></span>
							{/each}
						</div>
						<span class="text-xs text-muted-foreground">{session.rating_mood}/5</span>
					</div>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Exercise details -->
	{#each session.exercise_groups as group}
		{@const suggestion = getProgressionSuggestion(group)}
		<div class="rounded-lg border border-border bg-card p-4">
			<div class="mb-3 flex items-center justify-between">
				<div>
					<a
						href="/calendar/exercises/{group.exercise.id}"
						class="font-medium hover:text-primary hover:underline"
					>
						{group.exercise.name}
					</a>
					<span class="ml-2 text-xs text-muted-foreground">{group.exercise.category}</span>
				</div>
			</div>

			<div class="space-y-1">
				<div class="flex gap-4 text-xs font-medium text-muted-foreground px-2">
					<span class="w-10">Set</span>
					<span class="w-20">Weight</span>
					<span class="w-16">Reps</span>
					{#if group.sets.some((s) => s.rpe)}
						<span class="w-12">RPE</span>
					{/if}
				</div>
				{#each group.sets.filter((s) => s.completed) as set}
					<div class="flex gap-4 rounded px-2 py-1 text-sm">
						<span class="w-10 text-muted-foreground">{set.set_number}</span>
						<span class="w-20 font-medium tabular-nums">{set.weight_kg} kg</span>
						<span class="w-16 tabular-nums">{set.reps}</span>
						{#if group.sets.some((s) => s.rpe)}
							<span class="w-12 text-muted-foreground tabular-nums">
								{set.rpe ?? '—'}
							</span>
						{/if}
					</div>
				{/each}
			</div>

			{#if suggestion}
				<div class="mt-3 flex items-center gap-2 rounded-lg bg-green-500/10 px-3 py-2 text-sm text-green-700 dark:text-green-400">
					<TrendingUp class="h-4 w-4 shrink-0" />
					<span>{suggestion}</span>
				</div>
			{/if}
		</div>
	{/each}

	{#if session.notes}
		<div class="rounded-lg border border-border bg-card p-4">
			<h3 class="mb-2 text-sm font-medium text-muted-foreground">Notes</h3>
			<p class="text-sm">{session.notes}</p>
		</div>
	{/if}
</div>
