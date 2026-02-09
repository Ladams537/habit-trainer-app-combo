<script lang="ts">
	import type { CompetencyLevel } from '$lib/api/skills';

	let { levels }: { levels: CompetencyLevel[] } = $props();

	function barColor(r: number): string {
		if (r >= 0.8) return 'bg-green-500';
		if (r >= 0.5) return 'bg-yellow-500';
		return 'bg-red-500';
	}

	function formatDate(d: string | null): string {
		if (!d) return 'Never reviewed';
		const date = new Date(d);
		const now = new Date();
		const diff = date.getTime() - now.getTime();
		const days = Math.ceil(diff / 86400000);
		if (days <= 0) return 'Due now';
		if (days === 1) return 'Due tomorrow';
		return `Due in ${days} days`;
	}
</script>

<div class="space-y-2">
	{#each levels as level (level.id)}
		<div class="rounded-md border border-border p-3">
			<div class="mb-1.5 flex items-center justify-between">
				<span class="text-sm font-medium">{level.sub_skill}</span>
				<span class="text-xs text-muted-foreground">{formatDate(level.next_review_date)}</span>
			</div>
			<div class="flex items-center gap-2">
				<div class="h-2 flex-1 rounded-full bg-muted">
					<div
						class="h-full rounded-full transition-all {barColor(level.retrievability)}"
						style="width: {Math.round(level.retrievability * 100)}%"
					></div>
				</div>
				<span class="w-10 text-right text-xs tabular-nums text-muted-foreground">
					{Math.round(level.retrievability * 100)}%
				</span>
			</div>
			<div class="mt-1 flex gap-3 text-xs text-muted-foreground">
				<span>{level.review_count} review{level.review_count !== 1 ? 's' : ''}</span>
				<span>D:{level.difficulty.toFixed(1)}</span>
				<span>S:{level.stability.toFixed(1)}</span>
			</div>
		</div>
	{/each}
</div>
