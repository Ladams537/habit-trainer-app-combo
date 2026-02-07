<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';
	import type { MuscleGroupVolume } from '$lib/api/fitness';

	let { data }: { data: MuscleGroupVolume[] } = $props();

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

		// Already sorted desc from backend, reverse for horizontal bar (bottom-to-top)
		const sorted = [...data].reverse();
		const labels = sorted.map((d) => d.muscle_group);
		const volumes = sorted.map((d) => Math.round(d.volume));

		const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

		chart.setOption({
			grid: {
				left: 100,
				right: 24,
				top: 8,
				bottom: 24
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow' },
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 },
				formatter: (params: { name: string; value: number }[]) => {
					const p = params[0];
					return `${p.name}: ${p.value.toLocaleString()} kg`;
				}
			},
			xAxis: {
				type: 'value',
				axisLine: { show: false },
				axisLabel: { color: '#999', fontSize: 11 },
				splitLine: { lineStyle: { color: '#333' } }
			},
			yAxis: {
				type: 'category',
				data: labels,
				axisLine: { lineStyle: { color: '#666' } },
				axisLabel: { color: '#ccc', fontSize: 12 }
			},
			series: [
				{
					type: 'bar',
					data: volumes.map((v, i) => ({
						value: v,
						itemStyle: { color: colors[i % colors.length], borderRadius: [0, 4, 4, 0] }
					})),
					barMaxWidth: 24
				}
			]
		});
	}

	$effect(() => {
		data;
		updateChart();
	});
</script>

<div bind:this={chartContainer} class="w-full" style="height: {Math.max(160, data.length * 36)}px"></div>
