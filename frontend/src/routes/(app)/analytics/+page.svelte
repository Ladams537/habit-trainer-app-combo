<script lang="ts">
	import WeeklyVolumeChart from '$lib/components/fitness/WeeklyVolumeChart.svelte';
	import MuscleGroupChart from '$lib/components/fitness/MuscleGroupChart.svelte';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import Clock from '@lucide/svelte/icons/clock';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import Flame from '@lucide/svelte/icons/flame';
	import Weight from '@lucide/svelte/icons/weight';
	import BarChart3 from '@lucide/svelte/icons/bar-chart-3';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	let { data } = $props();

	const overview = data.overview;

	function formatDuration(startedAt: string, completedAt: string | null) {
		if (!completedAt) return 'In progress';
		const start = new Date(startedAt).getTime();
		const end = new Date(completedAt).getTime();
		const mins = Math.round((end - start) / 60000);
		if (mins < 60) return `${mins}m`;
		return `${Math.floor(mins / 60)}h ${mins % 60}m`;
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-GB', {
			weekday: 'short',
			day: 'numeric',
			month: 'short'
		});
	}
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold">Analytics</h1>

	{#if overview}
		<!-- Summary Stat Cards -->
		<div class="grid grid-cols-3 gap-3">
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Dumbbell class="h-4 w-4 text-blue-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{overview.total_workouts}</div>
				<div class="text-xs text-muted-foreground">Workouts</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Weight class="h-4 w-4 text-green-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">
					{overview.total_volume >= 1000
						? `${(overview.total_volume / 1000).toFixed(1)}t`
						: `${Math.round(overview.total_volume)}kg`}
				</div>
				<div class="text-xs text-muted-foreground">Total Volume</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Flame class="h-4 w-4 text-orange-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{overview.current_streak}</div>
				<div class="text-xs text-muted-foreground">Week Streak</div>
			</div>
		</div>

		<!-- Weekly Volume Chart -->
		{#if overview.weekly_volume.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<BarChart3 class="h-4 w-4" />
					Weekly Volume & Frequency
				</h2>
				<WeeklyVolumeChart weeks={overview.weekly_volume} />
			</div>
		{/if}

		<!-- Muscle Group Distribution -->
		{#if overview.muscle_group_volume.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<TrendingUp class="h-4 w-4" />
					Muscle Group Distribution
				</h2>
				<MuscleGroupChart data={overview.muscle_group_volume} />
			</div>
		{/if}
	{/if}

	<!-- Exercise Stats -->
	{#if data.trainedExercises.length > 0}
		<div class="space-y-3">
			<h2 class="flex items-center gap-2 text-lg font-semibold">
				<TrendingUp class="h-5 w-5" />
				Exercise Stats
			</h2>
			<div class="space-y-2">
				{#each data.trainedExercises as exercise (exercise.id)}
					<a
						href="/analytics/exercises/{exercise.id}"
						class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent"
					>
						<div class="flex-1 min-w-0">
							<div class="font-medium">{exercise.name}</div>
							<div class="text-xs text-muted-foreground">
								{exercise.category} · {exercise.muscle_groups.join(', ')}
							</div>
						</div>
						<ChevronRight class="h-4 w-4 text-muted-foreground" />
					</a>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Recent Sessions -->
	<div class="space-y-3">
		<h2 class="flex items-center gap-2 text-lg font-semibold">
			<Dumbbell class="h-5 w-5" />
			Workout History
		</h2>

		{#if data.sessions.length === 0}
			<div
				class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground"
			>
				<TrendingUp class="mx-auto mb-3 h-10 w-10 opacity-40" />
				<p class="mb-1 font-medium">No workouts yet</p>
				<p class="text-sm">Complete a workout to see your history here.</p>
			</div>
		{:else}
			<div class="space-y-2">
				{#each data.sessions as session (session.id)}
					<a
						href="/analytics/sessions/{session.id}"
						class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent"
					>
						<div class="flex-1 min-w-0">
							<div class="font-medium">
								{session.template_name || 'Free-form Workout'}
							</div>
							<div class="flex items-center gap-3 text-xs text-muted-foreground">
								<span>{formatDate(session.started_at)}</span>
								{#if session.completed_at}
									<span class="flex items-center gap-1">
										<Clock class="h-3 w-3" />
										{formatDuration(session.started_at, session.completed_at)}
									</span>
								{/if}
							</div>
						</div>
						<div class="text-right text-sm">
							<div class="tabular-nums">
								{session.exercise_count} exercise{session.exercise_count !== 1
									? 's'
									: ''}
							</div>
							<div class="text-xs text-muted-foreground tabular-nums">
								{session.total_sets} sets ·
								{Math.round(session.total_volume)}kg
							</div>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</div>
</div>
