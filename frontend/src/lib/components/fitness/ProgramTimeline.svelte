<script lang="ts">
	import type { ProgramWeek } from '$lib/api/programs';
	import CheckCircle from '@lucide/svelte/icons/check-circle';
	import Circle from '@lucide/svelte/icons/circle';
	import Play from '@lucide/svelte/icons/play';

	let { weeks, programId }: { weeks: ProgramWeek[]; programId: string } = $props();

	const statusIcons: Record<string, typeof Circle> = {
		active: Play,
		completed: CheckCircle,
		pending: Circle
	};

	const statusColors: Record<string, string> = {
		active: 'border-primary bg-primary/10 text-primary',
		completed: 'border-green-500 bg-green-500/10 text-green-500',
		pending: 'border-border bg-muted text-muted-foreground'
	};
</script>

<div class="space-y-2">
	{#each weeks as week (week.id)}
		{@const Icon = statusIcons[week.status] || Circle}
		<a
			href="/programs/{programId}/week/{week.week_number}"
			class="flex items-center gap-3 rounded-lg border px-4 py-3 transition-colors hover:bg-accent {statusColors[week.status] || 'border-border'}"
		>
			<Icon class="h-5 w-5 shrink-0" />
			<div class="flex-1 min-w-0">
				<div class="font-medium text-foreground">Week {week.week_number}</div>
				<div class="text-xs text-muted-foreground">
					{week.prescriptions.length} day{week.prescriptions.length !== 1 ? 's' : ''}
					{#if week.prescriptions.length > 0}
						· {week.prescriptions.map((d) => d.day_label).join(', ')}
					{/if}
				</div>
			</div>
			<span class="text-xs capitalize">{week.status}</span>
		</a>
	{/each}
</div>
