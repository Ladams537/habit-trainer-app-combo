<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import ProgramTimeline from '$lib/components/fitness/ProgramTimeline.svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Pause from '@lucide/svelte/icons/pause';
	import Play from '@lucide/svelte/icons/play';

	let { data } = $props();
	const program = data.program;
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/programs" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div class="flex-1">
			<h1 class="text-2xl font-bold">{program.name}</h1>
			{#if program.description}
				<p class="text-sm text-muted-foreground">{program.description}</p>
			{/if}
		</div>
	</div>

	<div class="flex items-center gap-2 text-sm">
		<span class="rounded-full px-2 py-0.5 text-xs font-medium
			{program.status === 'active' ? 'bg-green-500/10 text-green-500' :
			 program.status === 'paused' ? 'bg-yellow-500/10 text-yellow-500' :
			 'bg-muted text-muted-foreground'}">
			{program.status}
		</span>
		<span class="text-muted-foreground">{program.workouts_per_week}x/week</span>
		<span class="text-muted-foreground">{program.weeks.length} week{program.weeks.length !== 1 ? 's' : ''}</span>
	</div>

	{#if program.status === 'active'}
		<form method="POST" action="?/updateStatus" use:enhance>
			<input type="hidden" name="status" value="paused" />
			<Button type="submit" variant="outline" size="sm">
				<Pause class="mr-1 h-4 w-4" />
				Pause Program
			</Button>
		</form>
	{:else if program.status === 'paused'}
		<form method="POST" action="?/updateStatus" use:enhance>
			<input type="hidden" name="status" value="active" />
			<Button type="submit" variant="outline" size="sm">
				<Play class="mr-1 h-4 w-4" />
				Resume Program
			</Button>
		</form>
	{/if}

	<ProgramTimeline weeks={program.weeks} programId={program.id} />

	<Card.Root class="border-destructive/50">
		<Card.Content class="flex items-center justify-between py-4">
			<div>
				<p class="font-medium">Delete program</p>
				<p class="text-sm text-muted-foreground">This cannot be undone</p>
			</div>
			<form method="POST" action="?/delete" use:enhance>
				<Button type="submit" variant="destructive" size="sm">
					<Trash2 class="mr-1 h-4 w-4" />
					Delete
				</Button>
			</form>
		</Card.Content>
	</Card.Root>
</div>
