<script lang="ts">
	import type { WeeklySummary } from '$lib/api/programs';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';

	interface Props {
		summary: WeeklySummary;
	}

	let { summary }: Props = $props();
	let expanded = $state(false);

	const weekLabel = $derived(() => {
		const start = new Date(summary.week_start);
		const end = new Date(start);
		end.setDate(end.getDate() + 6);
		return `${start.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} — ${end.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}`;
	});
</script>

<button
	type="button"
	class="w-full text-left rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent"
	onclick={() => (expanded = !expanded)}
>
	<div class="flex items-center gap-3">
		<Dumbbell class="h-4 w-4 text-blue-500 shrink-0" />
		<div class="flex-1 min-w-0">
			<div class="font-medium text-sm">{weekLabel()}</div>
			<div class="flex items-center gap-3 text-xs text-muted-foreground">
				<span>{summary.session_count} workout{summary.session_count !== 1 ? 's' : ''}</span>
				<span>{Math.round(summary.total_volume)}kg volume</span>
				{#if summary.avg_rpe !== null}
					<span>RPE {summary.avg_rpe.toFixed(1)}</span>
				{/if}
			</div>
		</div>
		{#if expanded}
			<ChevronUp class="h-4 w-4 text-muted-foreground shrink-0" />
		{:else}
			<ChevronDown class="h-4 w-4 text-muted-foreground shrink-0" />
		{/if}
	</div>

	{#if expanded}
		<div class="mt-3 pt-3 border-t border-border space-y-2">
			{#if summary.exercises_trained.length > 0}
				<div>
					<div class="text-xs font-medium text-muted-foreground mb-1">Exercises trained</div>
					<div class="flex flex-wrap gap-1">
						{#each summary.exercises_trained as name}
							<span class="rounded-full bg-muted px-2 py-0.5 text-xs">{name}</span>
						{/each}
					</div>
				</div>
			{/if}
			{#if summary.avg_energy !== null}
				<div class="text-xs text-muted-foreground">
					Avg Energy: {summary.avg_energy.toFixed(1)}/5
				</div>
			{/if}
		</div>
	{/if}
</button>
