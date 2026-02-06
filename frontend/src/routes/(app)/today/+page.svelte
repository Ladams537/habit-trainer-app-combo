<script lang="ts">
	import HabitChecklist from '$lib/components/habits/HabitChecklist.svelte';
	import { Button } from '$lib/components/ui/button';
	import Plus from '@lucide/svelte/icons/plus';

	let { data } = $props();

	const today = new Date().toLocaleDateString('en-GB', {
		weekday: 'long',
		day: 'numeric',
		month: 'long'
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Today</h1>
			<p class="text-muted-foreground">{today}</p>
		</div>
		<Button href="/habits/new" variant="outline" size="sm">
			<Plus class="mr-1 h-4 w-4" />
			Add habit
		</Button>
	</div>

	<HabitChecklist habits={data.habits} />
</div>
