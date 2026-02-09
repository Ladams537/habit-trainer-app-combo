<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';
	import type { TrendSeries } from '$lib/api/analytics';

	let {
		series,
		colors = ['#3B82F6', '#F59E0B', '#22c55e', '#8B5CF6']
	}: { series: TrendSeries[]; colors?: string[] } = $props();

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
		if (!chart || series.length === 0) return;

		// Collect all unique dates
		const allDates = [
			...new Set(series.flatMap((s) => s.data.map((d) => d.date)))
		].sort();

		// Determine if we need dual Y-axes (different units)
		const uniqueUnits = [...new Set(series.map((s) => s.unit))];
		const needsDualAxis = uniqueUnits.length > 1;

		const yAxes = uniqueUnits.map((unit, i) => ({
			type: 'value' as const,
			name: unit,
			nameTextStyle: { color: '#999', fontSize: 11 },
			axisLine: { show: false },
			axisLabel: { color: '#999', fontSize: 11 },
			splitLine: { lineStyle: { color: '#333' }, show: i === 0 },
			position: i === 0 ? ('left' as const) : ('right' as const)
		}));

		const chartSeries = series.map((s, i) => {
			const dataMap = new Map(s.data.map((d) => [d.date, d.value]));
			return {
				name: s.metric.replace(/_/g, ' '),
				type: 'line' as const,
				smooth: true,
				symbol: 'circle',
				symbolSize: 5,
				yAxisIndex: needsDualAxis ? uniqueUnits.indexOf(s.unit) : 0,
				lineStyle: { color: colors[i % colors.length], width: 2 },
				itemStyle: { color: colors[i % colors.length] },
				areaStyle: series.length === 1 ? { color: colors[i % colors.length] + '20' } : undefined,
				data: allDates.map((d) => dataMap.get(d) ?? null)
			};
		});

		chart.setOption({
			grid: {
				left: 50,
				right: needsDualAxis ? 50 : 24,
				top: 24,
				bottom: 32
			},
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 }
			},
			legend:
				series.length > 1
					? {
							bottom: 0,
							textStyle: { color: '#999', fontSize: 11 },
							icon: 'circle',
							itemWidth: 8
						}
					: undefined,
			xAxis: {
				type: 'category',
				data: allDates.map((d) => {
					const dt = new Date(d);
					return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
				}),
				axisLine: { lineStyle: { color: '#666' } },
				axisLabel: { color: '#999', fontSize: 10, rotate: 30 }
			},
			yAxis: yAxes,
			series: chartSeries
		});
	}

	$effect(() => {
		series;
		updateChart();
	});
</script>

<div bind:this={chartContainer} class="h-64 w-full"></div>
