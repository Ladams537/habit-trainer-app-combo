<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Clock from '@lucide/svelte/icons/clock';

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
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/analytics" variant="ghost" size="sm">
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

	<!-- Exercise details -->
	{#each session.exercise_groups as group}
		<div class="rounded-lg border border-border bg-card p-4">
			<div class="mb-3 flex items-center justify-between">
				<div>
					<a
						href="/analytics/exercises/{group.exercise.id}"
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
		</div>
	{/each}

	{#if session.notes}
		<div class="rounded-lg border border-border bg-card p-4">
			<h3 class="mb-2 text-sm font-medium text-muted-foreground">Notes</h3>
			<p class="text-sm">{session.notes}</p>
		</div>
	{/if}
</div>
