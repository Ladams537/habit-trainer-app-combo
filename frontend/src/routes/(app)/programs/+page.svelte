<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import Plus from '@lucide/svelte/icons/plus';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import FileText from '@lucide/svelte/icons/file-text';
	import Pause from '@lucide/svelte/icons/pause';
	import CheckCircle from '@lucide/svelte/icons/check-circle';
	import Play from '@lucide/svelte/icons/play';

	let { data } = $props();

	const statusColors: Record<string, string> = {
		active: 'text-green-500',
		paused: 'text-yellow-500',
		completed: 'text-muted-foreground'
	};

	const statusIcons: Record<string, typeof Play> = {
		active: Play,
		paused: Pause,
		completed: CheckCircle
	};
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Programs</h1>
		<Button href="/programs/new" size="sm">
			<Plus class="mr-1 h-4 w-4" />
			New Program
		</Button>
	</div>

	{#if data.programs.length === 0}
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-12 text-center">
				<Dumbbell class="mb-3 h-10 w-10 text-muted-foreground/40" />
				<p class="mb-1 font-medium">No programs yet</p>
				<p class="mb-4 text-sm text-muted-foreground">
					Create a training program to get periodized progression with weekly planning.
				</p>
				<Button href="/programs/new">Create your first program</Button>
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="space-y-3">
			{#each data.programs as program (program.id)}
				{@const StatusIcon = statusIcons[program.status] || Play}
				<a
					href="/programs/{program.id}"
					class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent"
				>
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2">
							<StatusIcon class="h-4 w-4 {statusColors[program.status] || ''}" />
							<span class="font-medium">{program.name}</span>
						</div>
						<div class="text-xs text-muted-foreground mt-0.5">
							{program.workouts_per_week}x/week · {program.week_count} week{program.week_count !== 1 ? 's' : ''}
							{#if program.current_week}
								· Week {program.current_week}
							{/if}
						</div>
					</div>
					<ChevronRight class="h-4 w-4 text-muted-foreground" />
				</a>
			{/each}
		</div>
	{/if}

	<div class="pt-2">
		<a
			href="/programs/templates"
			class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
		>
			<FileText class="h-4 w-4" />
			Manage Templates
		</a>
	</div>
</div>
