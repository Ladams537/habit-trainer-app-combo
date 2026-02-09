<script lang="ts">
	import WeeklyVolumeChart from '$lib/components/fitness/WeeklyVolumeChart.svelte';
	import MuscleGroupChart from '$lib/components/fitness/MuscleGroupChart.svelte';
	import WeeklySummaryCard from '$lib/components/fitness/WeeklySummaryCard.svelte';
	import CalendarHeatmap from '$lib/components/analytics/CalendarHeatmap.svelte';
	import InsightCards from '$lib/components/analytics/InsightCards.svelte';
	import StreaksDashboard from '$lib/components/analytics/StreaksDashboard.svelte';
	import TrendChart from '$lib/components/analytics/TrendChart.svelte';
	import CorrelationScatter from '$lib/components/analytics/CorrelationScatter.svelte';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import Clock from '@lucide/svelte/icons/clock';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import Flame from '@lucide/svelte/icons/flame';
	import Weight from '@lucide/svelte/icons/weight';
	import BarChart3 from '@lucide/svelte/icons/bar-chart-3';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Activity from '@lucide/svelte/icons/activity';
	import Heart from '@lucide/svelte/icons/heart';
	import BookOpen from '@lucide/svelte/icons/book-open';
	import Layers from '@lucide/svelte/icons/layers';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import { Button } from '$lib/components/ui/button';

	let { data } = $props();

	const overview = data.overview;
	const dashboard = data.dashboard;

	type Tab = 'overview' | 'fitness' | 'habits' | 'skills' | 'cross-domain';
	let activeTab = $state<Tab>('overview');

	const tabs: { id: Tab; label: string; icon: typeof Activity }[] = [
		{ id: 'overview', label: 'Overview', icon: Activity },
		{ id: 'fitness', label: 'Fitness', icon: Dumbbell },
		{ id: 'habits', label: 'Habits', icon: Heart },
		{ id: 'skills', label: 'Skills', icon: BookOpen },
		{ id: 'cross-domain', label: 'Cross-domain', icon: Layers }
	];

	// Derived data for tabs
	const habitsStreaks = $derived(
		dashboard?.streaks.streaks.filter((s) => s.domain === 'habits') ?? []
	);
	const habitsCompletionSeries = $derived(
		data.habitsTrends?.series.filter((s) => s.metric === 'completion_rate') ?? []
	);
	const skillsPracticeSeries = $derived(
		data.skillsTrends?.series.filter((s) => s.metric === 'practice_minutes') ?? []
	);

	// Habits stats
	const habitCount = $derived(habitsStreaks.length);
	const avgStrength = $derived(
		habitsStreaks.length > 0
			? Math.round(
					(habitsStreaks.reduce((s, h) => s + (h.strength ?? 0), 0) / habitsStreaks.length) * 100
				)
			: 0
	);
	const bestStreak = $derived(
		habitsStreaks.length > 0 ? Math.max(...habitsStreaks.map((h) => h.longest_streak)) : 0
	);

	// Skills stats
	const skillsStreaks = $derived(
		dashboard?.streaks.streaks.filter((s) => s.domain === 'skills') ?? []
	);
	const skillCount = $derived(skillsStreaks.length);
	const totalPracticeHours = $derived(() => {
		const series = data.skillsTrends?.series.find((s) => s.metric === 'practice_minutes');
		if (!series) return 0;
		const totalMins = series.data.reduce((s, p) => s + p.value, 0);
		return Math.round(totalMins / 60);
	});

	// Cross-domain overlay: habits completion + fitness volume
	const crossDomainSeries = $derived(() => {
		const result = [];
		const habitsRate = data.habitsTrends?.series.find((s) => s.metric === 'completion_rate');
		if (habitsRate) result.push(habitsRate);
		if (overview?.weekly_volume) {
			result.push({
				metric: 'volume',
				unit: 'kg',
				data: overview.weekly_volume.map((w) => ({
					date: w.week_start,
					value: Math.round(w.total_volume)
				}))
			});
		}
		return result;
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Analytics</h1>
		<Button href="/calendar" variant="outline" size="sm">
			<CalendarDays class="mr-1 h-4 w-4" />
			Calendar
		</Button>
	</div>

	<!-- Tab Navigation -->
	<div class="flex gap-1 overflow-x-auto pb-1 scrollbar-none">
		{#each tabs as tab (tab.id)}
			{@const Icon = tab.icon}
			<button
				class="flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors
					{activeTab === tab.id
					? 'bg-primary text-primary-foreground'
					: 'text-muted-foreground hover:bg-accent hover:text-foreground'}"
				onclick={() => (activeTab = tab.id)}
			>
				<Icon class="h-3.5 w-3.5" />
				{tab.label}
			</button>
		{/each}
	</div>

	<!-- Overview Tab -->
	{#if activeTab === 'overview'}
		{#if dashboard}
			{#if dashboard.insights.length > 0}
				<InsightCards insights={dashboard.insights} />
			{/if}

			{#if dashboard.heatmap.days.length > 0}
				<div class="rounded-lg border border-border bg-card p-4">
					<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
						<Activity class="h-4 w-4" />
						Activity
					</h2>
					<CalendarHeatmap days={dashboard.heatmap.days} year={dashboard.heatmap.year} />
				</div>
			{/if}

			{#if dashboard.streaks.streaks.length > 0}
				<div class="rounded-lg border border-border bg-card p-4 space-y-4">
					<h2 class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
						<Flame class="h-4 w-4" />
						Streaks
						{#if dashboard.streaks.total_active > 0}
							<span class="ml-auto text-xs tabular-nums">{dashboard.streaks.total_active} active</span>
						{/if}
					</h2>
					<StreaksDashboard streaks={dashboard.streaks.streaks} />
				</div>
			{/if}
		{:else}
			<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
				<Activity class="mx-auto mb-3 h-10 w-10 opacity-40" />
				<p class="mb-1 font-medium">No analytics data yet</p>
				<p class="text-sm">Start logging habits, workouts, or skills to see insights here.</p>
			</div>
		{/if}

	<!-- Fitness Tab -->
	{:else if activeTab === 'fitness'}
		{#if overview}
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

			{#if overview.weekly_volume.length > 0}
				<div class="rounded-lg border border-border bg-card p-4">
					<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
						<BarChart3 class="h-4 w-4" />
						Weekly Volume & Frequency
					</h2>
					<WeeklyVolumeChart weeks={overview.weekly_volume} />
				</div>
			{/if}

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

		{#if data.trainedExercises.length > 0}
			<div class="space-y-3">
				<h2 class="flex items-center gap-2 text-lg font-semibold">
					<TrendingUp class="h-5 w-5" />
					Exercise Stats
				</h2>
				<div class="space-y-2">
					{#each data.trainedExercises as exercise (exercise.id)}
						<a
							href="/calendar/exercises/{exercise.id}"
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

		<!-- Weekly Summaries (replaces Workout History) -->
		<div class="space-y-3">
			<div class="flex items-center justify-between">
				<h2 class="flex items-center gap-2 text-lg font-semibold">
					<Dumbbell class="h-5 w-5" />
					Weekly Summaries
				</h2>
				<span class="text-xs text-muted-foreground">View individual workouts on the Calendar page</span>
			</div>

			{#if data.weeklySummaries.length === 0}
				<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
					<TrendingUp class="mx-auto mb-3 h-10 w-10 opacity-40" />
					<p class="mb-1 font-medium">No workouts yet</p>
					<p class="text-sm">Complete a workout to see weekly summaries here.</p>
				</div>
			{:else}
				<div class="space-y-2">
					{#each data.weeklySummaries as summary (summary.week_start)}
						<WeeklySummaryCard {summary} />
					{/each}
				</div>
			{/if}
		</div>

	<!-- Habits Tab -->
	{:else if activeTab === 'habits'}
		<div class="grid grid-cols-3 gap-3">
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Heart class="h-4 w-4 text-green-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{habitCount}</div>
				<div class="text-xs text-muted-foreground">Active</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<TrendingUp class="h-4 w-4 text-green-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{avgStrength}%</div>
				<div class="text-xs text-muted-foreground">Avg Strength</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Flame class="h-4 w-4 text-orange-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{bestStreak}</div>
				<div class="text-xs text-muted-foreground">Best Streak</div>
			</div>
		</div>

		{#if habitsCompletionSeries.length > 0 && habitsCompletionSeries[0].data.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<BarChart3 class="h-4 w-4" />
					Completion Rate
				</h2>
				<TrendChart series={habitsCompletionSeries} colors={['#22c55e']} />
			</div>
		{/if}

		{#if habitsStreaks.length > 0}
			<div class="rounded-lg border border-border bg-card p-4 space-y-4">
				<h2 class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<Flame class="h-4 w-4" />
					Habit Streaks
				</h2>
				<StreaksDashboard streaks={habitsStreaks} />
			</div>
		{/if}

	<!-- Skills Tab -->
	{:else if activeTab === 'skills'}
		<div class="grid grid-cols-3 gap-3">
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<BookOpen class="h-4 w-4 text-purple-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{skillCount}</div>
				<div class="text-xs text-muted-foreground">Active</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Clock class="h-4 w-4 text-purple-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">{totalPracticeHours()}</div>
				<div class="text-xs text-muted-foreground">Total Hours</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<div class="mb-1 flex items-center justify-center">
					<Flame class="h-4 w-4 text-orange-500" />
				</div>
				<div class="text-2xl font-bold tabular-nums">
					{skillsStreaks.length > 0 ? Math.max(...skillsStreaks.map((s) => s.current_streak)) : 0}
				</div>
				<div class="text-xs text-muted-foreground">Best Streak</div>
			</div>
		</div>

		{#if skillsPracticeSeries.length > 0 && skillsPracticeSeries[0].data.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<BarChart3 class="h-4 w-4" />
					Practice Minutes
				</h2>
				<TrendChart series={skillsPracticeSeries} colors={['#8B5CF6']} />
			</div>
		{/if}

	<!-- Cross-domain Tab -->
	{:else if activeTab === 'cross-domain'}
		{#if data.correlations && data.correlations.data.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<Layers class="h-4 w-4" />
					Habit Consistency vs Training Volume
				</h2>
				<CorrelationScatter
					data={data.correlations.data}
					xLabel={data.correlations.x_label}
					yLabel={data.correlations.y_label}
					correlation={data.correlations.correlation_coefficient}
				/>
			</div>
		{/if}

		{@const cdSeries = crossDomainSeries()}
		{#if cdSeries.length > 0}
			<div class="rounded-lg border border-border bg-card p-4">
				<h2 class="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
					<TrendingUp class="h-4 w-4" />
					Habits + Fitness Overlay
				</h2>
				<TrendChart series={cdSeries} colors={['#22c55e', '#3B82F6']} />
			</div>
		{/if}

		{#if !data.correlations?.data?.length && crossDomainSeries().length === 0}
			<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
				<Layers class="mx-auto mb-3 h-10 w-10 opacity-40" />
				<p class="mb-1 font-medium">Not enough data yet</p>
				<p class="text-sm">Log activities across multiple domains to see cross-domain insights.</p>
			</div>
		{/if}
	{/if}
</div>
