<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';

	let {
		dates,
		values,
		label = 'Weight (kg)',
		color = '#3B82F6'
	}: {
		dates: string[];
		values: number[];
		label?: string;
		color?: string;
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
		if (!chart) return;

		chart.setOption({
			grid: {
				left: 50,
				right: 16,
				top: 16,
				bottom: 32
			},
			xAxis: {
				type: 'category',
				data: dates.map((d) => {
					const date = new Date(d);
					return `${date.getMonth() + 1}/${date.getDate()}`;
				}),
				axisLine: { lineStyle: { color: '#666' } },
				axisLabel: { color: '#999', fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				name: label,
				nameTextStyle: { color: '#999', fontSize: 11 },
				axisLine: { show: false },
				axisLabel: { color: '#999', fontSize: 11 },
				splitLine: { lineStyle: { color: '#333' } }
			},
			series: [
				{
					data: values,
					type: 'line',
					smooth: true,
					symbol: 'circle',
					symbolSize: 8,
					lineStyle: { color, width: 2 },
					itemStyle: { color },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
							{ offset: 0, color: color + '40' },
							{ offset: 1, color: color + '05' }
						])
					}
				}
			],
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1a1a1a',
				borderColor: '#333',
				textStyle: { color: '#fff', fontSize: 12 }
			}
		});
	}

	$effect(() => {
		// Re-render when data changes
		dates;
		values;
		updateChart();
	});
</script>

<div bind:this={chartContainer} class="h-64 w-full"></div>
