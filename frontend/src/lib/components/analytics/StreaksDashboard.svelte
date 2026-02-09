<script lang="ts">
	import type { StreakItem } from '$lib/api/analytics';
	import Flame from '@lucide/svelte/icons/flame';

	let { streaks }: { streaks: StreakItem[] } = $props();

	const domainColors: Record<string, string> = {
		fitness: '#3B82F6',
		habits: '#22c55e',
		skills: '#8B5CF6'
	};

	const domainLabels: Record<string, string> = {
		fitness: 'Fitness',
		habits: 'Habits',
		skills: 'Skills'
	};

	function groupedStreaks() {
		const groups: Record<string, StreakItem[]> = {};
		for (const s of streaks) {
			if (!groups[s.domain]) groups[s.domain] = [];
			groups[s.domain].push(s);
		}
		return groups;
	}
</script>

{#each Object.entries(groupedStreaks()) as [domain, items] (domain)}
	<div class="space-y-2">
		<h3 class="text-xs font-medium uppercase tracking-wider text-muted-foreground">
			{domainLabels[domain] || domain}
		</h3>
		<div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
			{#each items as item (item.name)}
				<div
					class="flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2"
				>
					<Flame
						class="h-4 w-4 flex-shrink-0"
						style="color: {domainColors[domain] || '#999'}"
					/>
					<div class="min-w-0 flex-1">
						<div class="truncate text-sm font-medium">{item.name}</div>
						<div class="flex items-center gap-2 text-xs text-muted-foreground">
							<span>{item.current_streak}d current</span>
							<span class="text-border">|</span>
							<span>{item.longest_streak}d best</span>
						</div>
					</div>
					{#if item.strength != null}
						<div class="flex flex-col items-end gap-1">
							<span class="text-xs tabular-nums text-muted-foreground">
								{Math.round(item.strength * 100)}%
							</span>
							<div class="h-1.5 w-12 overflow-hidden rounded-full bg-muted">
								<div
									class="h-full rounded-full transition-all"
									style="width: {item.strength * 100}%; background: {domainColors[domain]}"
								></div>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
{/each}
