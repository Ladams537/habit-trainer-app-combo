<script lang="ts">
	import type { InsightCard } from '$lib/api/analytics';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import TrendingDown from '@lucide/svelte/icons/trending-down';
	import Trophy from '@lucide/svelte/icons/trophy';
	import BatteryLow from '@lucide/svelte/icons/battery-low';
	import AlertCircle from '@lucide/svelte/icons/circle-alert';
	import Link from '@lucide/svelte/icons/link';

	let { insights }: { insights: InsightCard[] } = $props();

	const iconMap: Record<string, typeof TrendingUp> = {
		'trending-up': TrendingUp,
		'trending-down': TrendingDown,
		trophy: Trophy,
		'battery-low': BatteryLow,
		'alert-circle': AlertCircle,
		link: Link
	};
</script>

{#if insights.length > 0}
	<div class="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-none">
		{#each insights as insight (insight.id)}
			{@const IconComponent = iconMap[insight.icon] || AlertCircle}
			<div
				class="flex min-w-[260px] flex-shrink-0 gap-3 rounded-lg border border-border bg-card p-4"
				style="border-left: 3px solid {insight.color}"
			>
				<div class="flex-shrink-0 mt-0.5">
					<IconComponent class="h-5 w-5" style="color: {insight.color}" />
				</div>
				<div class="min-w-0">
					<div class="font-medium text-sm">{insight.title}</div>
					<div class="text-xs text-muted-foreground mt-0.5">{insight.message}</div>
				</div>
			</div>
		{/each}
	</div>
{/if}
