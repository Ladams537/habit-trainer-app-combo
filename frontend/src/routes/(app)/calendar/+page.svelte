<script lang="ts">
	import { goto } from '$app/navigation';
	import MonthCalendar from '$lib/components/calendar/MonthCalendar.svelte';
	import { Button } from '$lib/components/ui/button';
	import ChartLine from '@lucide/svelte/icons/chart-line';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import Target from '@lucide/svelte/icons/target';
	import Clock from '@lucide/svelte/icons/clock';

	let { data } = $props();

	const summaryStats = $derived(() => {
		const summaries = data.weeklySummaries ?? [];
		if (summaries.length === 0) return null;

		const totalSessions = summaries.reduce((sum, w) => sum + w.session_count, 0);
		const totalVolume = summaries.reduce((sum, w) => sum + w.total_volume, 0);
		const avgRpe = summaries.filter((w) => w.avg_rpe !== null);
		const meanRpe =
			avgRpe.length > 0
				? avgRpe.reduce((sum, w) => sum + (w.avg_rpe ?? 0), 0) / avgRpe.length
				: null;

		return {
			workouts: totalSessions,
			volume: Math.round(totalVolume),
			avgRpe: meanRpe ? meanRpe.toFixed(1) : null
		};
	});

	function handleNavigate(year: number, month: number) {
		goto(`/calendar?year=${year}&month=${month}`);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Calendar</h1>
		<Button href="/analytics" variant="outline" size="sm">
			<ChartLine class="mr-1 h-4 w-4" />
			Analytics
		</Button>
	</div>

	<!-- Weekly summary stats -->
	{#if summaryStats()}
		{@const stats = summaryStats()!}
		<div class="grid grid-cols-3 gap-3">
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<Dumbbell class="mx-auto mb-1 h-4 w-4 text-blue-500" />
				<div class="text-lg font-bold">{stats.workouts}</div>
				<div class="text-xs text-muted-foreground">Workouts</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<Target class="mx-auto mb-1 h-4 w-4 text-green-500" />
				<div class="text-lg font-bold">{(stats.volume / 1000).toFixed(1)}k</div>
				<div class="text-xs text-muted-foreground">Volume (kg)</div>
			</div>
			<div class="rounded-lg border border-border bg-card p-3 text-center">
				<Clock class="mx-auto mb-1 h-4 w-4 text-amber-500" />
				<div class="text-lg font-bold">{stats.avgRpe ?? '—'}</div>
				<div class="text-xs text-muted-foreground">Avg RPE</div>
			</div>
		</div>
	{/if}

	<!-- Month calendar -->
	<div class="rounded-lg border border-border bg-card p-4">
		{#if data.calendar}
			<MonthCalendar
				days={data.calendar.days}
				currentMonth={data.month ?? new Date().getMonth() + 1}
				currentYear={data.year ?? new Date().getFullYear()}
				onNavigate={handleNavigate}
			/>
		{:else}
			<p class="text-center text-sm text-muted-foreground">Unable to load calendar data.</p>
		{/if}
	</div>
</div>
