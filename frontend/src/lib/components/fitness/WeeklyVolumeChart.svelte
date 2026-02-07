<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';
	import type { WeeklyVolume } from '$lib/api/fitness';

	let { weeks }: { weeks: WeeklyVolume[] } = $props();

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

		const labels = weeks.map((w) => {
			const d = new Date(w.week_start);
			return `${d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}`;
		});
		const volumes = weeks.map((w) => Math.round(w.total_volume));
		const counts = weeks.map((w) => w.session_count);

		chart.setOption({
			grid: {
				left: 50,
				right: 50,
				top: 24,
				bottom: 32
			},
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 }
			},
			xAxis: {
				type: 'category',
				data: labels,
				axisLine: { lineStyle: { color: '#666' } },
				axisLabel: { color: '#999', fontSize: 10, rotate: 30 }
			},
			yAxis: [
				{
					type: 'value',
					name: 'Volume (kg)',
					nameTextStyle: { color: '#999', fontSize: 11 },
					axisLine: { show: false },
					axisLabel: { color: '#999', fontSize: 11 },
					splitLine: { lineStyle: { color: '#333' } }
				},
				{
					type: 'value',
					name: 'Sessions',
					nameTextStyle: { color: '#999', fontSize: 11 },
					axisLine: { show: false },
					axisLabel: { color: '#999', fontSize: 11 },
					splitLine: { show: false },
					minInterval: 1
				}
			],
			series: [
				{
					name: 'Volume',
					data: volumes,
					type: 'bar',
					itemStyle: { color: '#3B82F6', borderRadius: [4, 4, 0, 0] },
					barMaxWidth: 32
				},
				{
					name: 'Sessions',
					data: counts,
					type: 'line',
					yAxisIndex: 1,
					smooth: true,
					symbol: 'circle',
					symbolSize: 6,
					lineStyle: { color: '#F59E0B', width: 2 },
					itemStyle: { color: '#F59E0B' }
				}
			]
		});
	}

	$effect(() => {
		weeks;
		updateChart();
	});
</script>

<div bind:this={chartContainer} class="h-64 w-full"></div>
