<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';
	import type { CorrelationPoint } from '$lib/api/analytics';

	let {
		data,
		xLabel,
		yLabel,
		correlation
	}: {
		data: CorrelationPoint[];
		xLabel: string;
		yLabel: string;
		correlation: number | null;
	} = $props();

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
		if (!chart || data.length === 0) return;

		const scatterData = data.map((d) => [d.x_value, d.y_value]);

		// Simple linear regression for trend line
		const xVals = data.map((d) => d.x_value);
		const yVals = data.map((d) => d.y_value);
		const n = xVals.length;
		const xMean = xVals.reduce((a, b) => a + b, 0) / n;
		const yMean = yVals.reduce((a, b) => a + b, 0) / n;
		const num = xVals.reduce((s, x, i) => s + (x - xMean) * (yVals[i] - yMean), 0);
		const den = xVals.reduce((s, x) => s + (x - xMean) ** 2, 0);
		const slope = den !== 0 ? num / den : 0;
		const intercept = yMean - slope * xMean;

		const xMin = Math.min(...xVals);
		const xMax = Math.max(...xVals);
		const lineData = [
			[xMin, slope * xMin + intercept],
			[xMax, slope * xMax + intercept]
		];

		const seriesList: echarts.EChartsOption['series'] = [
			{
				type: 'scatter',
				data: scatterData,
				symbolSize: 10,
				itemStyle: { color: '#3B82F6', opacity: 0.7 }
			}
		];

		if (n >= 3) {
			seriesList.push({
				type: 'line',
				data: lineData,
				symbol: 'none',
				lineStyle: { color: '#F59E0B', width: 2, type: 'dashed' },
				silent: true
			});
		}

		chart.setOption({
			grid: {
				left: 60,
				right: 24,
				top: 32,
				bottom: 40
			},
			tooltip: {
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 },
				formatter(params: { value: [number, number] } | { value: [number, number] }[]) {
					const p = Array.isArray(params) ? params[0] : params;
					if (!p?.value) return '';
					return `${xLabel}: ${p.value[0].toFixed(1)}<br/>${yLabel}: ${p.value[1].toFixed(1)}`;
				}
			},
			xAxis: {
				type: 'value',
				name: xLabel,
				nameLocation: 'center',
				nameGap: 28,
				nameTextStyle: { color: '#999', fontSize: 11 },
				axisLine: { lineStyle: { color: '#666' } },
				axisLabel: { color: '#999', fontSize: 11 },
				splitLine: { lineStyle: { color: '#333' } }
			},
			yAxis: {
				type: 'value',
				name: yLabel,
				nameTextStyle: { color: '#999', fontSize: 11 },
				axisLine: { show: false },
				axisLabel: { color: '#999', fontSize: 11 },
				splitLine: { lineStyle: { color: '#333' } }
			},
			series: seriesList
		});
	}

	$effect(() => {
		data;
		updateChart();
	});
</script>

<div class="space-y-2">
	{#if correlation != null}
		<div class="text-center text-xs text-muted-foreground">
			Pearson r = <span class="font-mono font-medium text-foreground">{correlation.toFixed(3)}</span>
			{#if Math.abs(correlation) >= 0.7}
				<span class="ml-1 text-green-500">(strong)</span>
			{:else if Math.abs(correlation) >= 0.4}
				<span class="ml-1 text-yellow-500">(moderate)</span>
			{:else}
				<span class="ml-1 text-muted-foreground">(weak)</span>
			{/if}
		</div>
	{/if}
	<div bind:this={chartContainer} class="h-64 w-full"></div>
</div>
