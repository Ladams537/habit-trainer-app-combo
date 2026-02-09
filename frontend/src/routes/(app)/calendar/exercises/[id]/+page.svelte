<script lang="ts">
	import ProgressionChart from '$lib/components/fitness/ProgressionChart.svelte';
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Trophy from '@lucide/svelte/icons/trophy';
	import Target from '@lucide/svelte/icons/target';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';
	import ArrowDown from '@lucide/svelte/icons/arrow-down';
	import type { ExerciseProgressionPoint } from '$lib/api/fitness';

	let { data } = $props();

	const { exercise, progression: allProgression } = data.stats;

	type RangeKey = '1M' | '3M' | '6M' | '1Y' | 'All';
	const ranges: { key: RangeKey; label: string; months: number | null }[] = [
		{ key: '1M', label: '1M', months: 1 },
		{ key: '3M', label: '3M', months: 3 },
		{ key: '6M', label: '6M', months: 6 },
		{ key: '1Y', label: '1Y', months: 12 },
		{ key: 'All', label: 'All', months: null }
	];

	let selectedRange: RangeKey = $state('All');

	const filtered = $derived.by(() => {
		const range = ranges.find((r) => r.key === selectedRange)!;
		if (!range.months) return allProgression;

		const cutoff = new Date();
		cutoff.setMonth(cutoff.getMonth() - range.months);
		return allProgression.filter((p) => new Date(p.date) >= cutoff);
	});

	const stats = $derived.by(() => {
		const prog = filtered;
		const totalSessions = prog.length;
		const prWeight = prog.length > 0 ? Math.max(...prog.map((p) => p.max_weight)) : 0;
		const totalVolume = prog.reduce((sum, p) => sum + p.volume, 0);
		const maxEstimated1rm = prog.length > 0 ? Math.max(...prog.map((p) => p.estimated_1rm)) : 0;
		return { totalSessions, prWeight, totalVolume, maxEstimated1rm };
	});

	const dates = $derived(filtered.map((p) => p.date));
	const maxWeights = $derived(filtered.map((p) => p.max_weight));
	const volumes = $derived(filtered.map((p) => Math.round(p.volume)));
	const estimated1RMs = $derived(filtered.map((p) => Math.round(p.estimated_1rm)));

	const sessionsWithDeltas = $derived.by(() => {
		const reversed = filtered.slice().reverse();
		return reversed.map((point, i) => {
			const prev = reversed[i + 1] as ExerciseProgressionPoint | undefined;
			let weightDelta: number | null = null;
			let volumeDelta: number | null = null;

			if (prev) {
				if (prev.max_weight !== 0) {
					weightDelta = ((point.max_weight - prev.max_weight) / prev.max_weight) * 100;
				}
				if (prev.volume !== 0) {
					volumeDelta = ((point.volume - prev.volume) / prev.volume) * 100;
				}
			}

			return { ...point, weightDelta, volumeDelta };
		});
	});
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/calendar" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div>
			<h1 class="text-2xl font-bold">{exercise.name}</h1>
			<p class="text-sm text-muted-foreground">
				{exercise.category} · {exercise.muscle_groups.join(', ')}
			</p>
		</div>
	</div>

	<!-- Time Range Filter -->
	<div class="flex gap-2">
		{#each ranges as range (range.key)}
			<button
				class="rounded-full px-3 py-1 text-sm font-medium transition-colors {selectedRange === range.key
					? 'bg-primary text-primary-foreground'
					: 'bg-muted text-muted-foreground hover:bg-accent'}"
				onclick={() => (selectedRange = range.key)}
			>
				{range.label}
			</button>
		{/each}
	</div>

	<!-- Stats cards -->
	<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="text-2xl font-bold tabular-nums">{stats.totalSessions}</div>
			<div class="text-xs text-muted-foreground">Sessions</div>
		</div>
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="flex items-center justify-center gap-1">
				<Trophy class="h-4 w-4 text-yellow-500" />
				<span class="text-2xl font-bold tabular-nums">{stats.prWeight}</span>
			</div>
			<div class="text-xs text-muted-foreground">PR Weight (kg)</div>
		</div>
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="text-2xl font-bold tabular-nums">{Math.round(stats.totalVolume)}</div>
			<div class="text-xs text-muted-foreground">Total Vol (kg)</div>
		</div>
		<div class="rounded-lg border border-border bg-card p-3 text-center">
			<div class="flex items-center justify-center gap-1">
				<Target class="h-4 w-4 text-amber-500" />
				<span class="text-2xl font-bold tabular-nums">{Math.round(stats.maxEstimated1rm)}</span>
			</div>
			<div class="text-xs text-muted-foreground">Est. 1RM (kg)</div>
		</div>
	</div>

	{#if filtered.length >= 2}
		<div class="rounded-lg border border-border bg-card p-4">
			<h2 class="mb-3 text-sm font-medium text-muted-foreground">Weight Progression</h2>
			<ProgressionChart {dates} values={maxWeights} label="Max Weight (kg)" />
		</div>

		<div class="rounded-lg border border-border bg-card p-4">
			<h2 class="mb-3 text-sm font-medium text-muted-foreground">Volume Per Session</h2>
			<ProgressionChart {dates} values={volumes} label="Volume (kg)" color="#10B981" />
		</div>

		<div class="rounded-lg border border-border bg-card p-4">
			<h2 class="mb-3 text-sm font-medium text-muted-foreground">Estimated 1RM</h2>
			<ProgressionChart {dates} values={estimated1RMs} label="Est. 1RM (kg)" color="#F59E0B" />
		</div>
	{:else if filtered.length === 1}
		<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
			<p class="text-sm">
				{#if selectedRange === 'All'}
					Complete at least 2 sessions with this exercise to see progression charts.
				{:else}
					Only 1 session in this time range. Try a wider range or complete more workouts.
				{/if}
			</p>
		</div>
	{:else}
		<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
			<p class="text-sm">
				{#if selectedRange === 'All'}
					No data yet. Log sets for this exercise to see your progression.
				{:else}
					No sessions in this time range. Try a wider range.
				{/if}
			</p>
		</div>
	{/if}

	{#if sessionsWithDeltas.length > 0}
		<div class="space-y-3">
			<h2 class="text-lg font-semibold">Recent Sessions</h2>
			<div class="space-y-2">
				{#each sessionsWithDeltas as point}
					<div class="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3">
						<div class="text-sm">
							{new Date(point.date).toLocaleDateString('en-GB', {
								day: 'numeric',
								month: 'short',
								year: 'numeric'
							})}
						</div>
						<div class="flex items-center gap-4 text-sm tabular-nums">
							<span class="flex items-center gap-1">
								<span class="text-muted-foreground">Best:</span>
								{point.best_set_weight}kg x {point.best_set_reps}
								{#if point.weightDelta !== null}
									{#if point.weightDelta > 0}
										<span class="flex items-center text-xs text-green-500">
											<ArrowUp class="h-3 w-3" />
											{point.weightDelta.toFixed(0)}%
										</span>
									{:else if point.weightDelta < 0}
										<span class="flex items-center text-xs text-red-500">
											<ArrowDown class="h-3 w-3" />
											{Math.abs(point.weightDelta).toFixed(0)}%
										</span>
									{:else}
										<span class="text-xs text-muted-foreground">—</span>
									{/if}
								{/if}
							</span>
							<span class="flex items-center gap-1">
								<span class="text-muted-foreground">Vol:</span>
								{Math.round(point.volume)}kg
								{#if point.volumeDelta !== null}
									{#if point.volumeDelta > 0}
										<span class="flex items-center text-xs text-green-500">
											<ArrowUp class="h-3 w-3" />
											{point.volumeDelta.toFixed(0)}%
										</span>
									{:else if point.volumeDelta < 0}
										<span class="flex items-center text-xs text-red-500">
											<ArrowDown class="h-3 w-3" />
											{Math.abs(point.volumeDelta).toFixed(0)}%
										</span>
									{:else}
										<span class="text-xs text-muted-foreground">—</span>
									{/if}
								{/if}
							</span>
							<span class="text-xs text-muted-foreground">
								{point.sets_count} sets
							</span>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
