<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';
	import type { HeatmapDay } from '$lib/api/analytics';

	let { days, year }: { days: HeatmapDay[]; year: number } = $props();

	let chartContainer: HTMLDivElement;
	let chart: echarts.ECharts | null = null;

	onMount(() => {
		chart = echarts.init(chartContainer);
		updateChart();

		const resizeObserver = new ResizeObserver(() => {
			chart?.resize();
		});
		resizeObserver.observe(chartContainer);

		return () => {
			resizeObserver.disconnect();
			chart?.dispose();
		};
	});

	function updateChart() {
		if (!chart) return;

		const data = days.map((d) => [d.date, d.count]);
		const maxCount = Math.max(...days.map((d) => d.count), 1);

		chart.setOption({
			tooltip: {
				position: 'top',
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 },
				formatter(params: { value: [string, number] }) {
					const day = days.find((d) => d.date === params.value[0]);
					if (!day) return params.value[0];
					const parts = [];
					if (day.fitness_count) parts.push(`Fitness: ${day.fitness_count}`);
					if (day.habits_count) parts.push(`Habits: ${day.habits_count}`);
					if (day.skills_count) parts.push(`Skills: ${day.skills_count}`);
					return `<strong>${params.value[0]}</strong><br/>${parts.join('<br/>') || 'No activity'}`;
				}
			},
			visualMap: {
				show: false,
				min: 0,
				max: maxCount,
				inRange: {
					color: ['#1a1a1a', '#0e4429', '#006d32', '#26a641', '#39d353']
				}
			},
			calendar: {
				top: 24,
				left: 40,
				right: 12,
				bottom: 8,
				range: String(year),
				cellSize: ['auto', 14],
				splitLine: { show: false },
				itemStyle: {
					borderWidth: 3,
					borderColor: 'transparent',
					color: '#161b22'
				},
				yearLabel: { show: false },
				monthLabel: {
					color: '#999',
					fontSize: 11,
					nameMap: 'en'
				},
				dayLabel: {
					color: '#999',
					fontSize: 10,
					nameMap: ['', 'M', '', 'W', '', 'F', '']
				}
			},
			series: [
				{
					type: 'heatmap',
					coordinateSystem: 'calendar',
					data
				}
			]
		});
	}

	$effect(() => {
		days;
		year;
		updateChart();
	});
</script>

<div bind:this={chartContainer} class="h-40 w-full"></div>
