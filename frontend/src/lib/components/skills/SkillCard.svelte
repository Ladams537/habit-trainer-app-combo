<script lang="ts">
	import type { SkillToday } from '$lib/api/skills';
	import Brain from '@lucide/svelte/icons/brain';

	let { skill }: { skill: SkillToday } = $props();

	const hours = $derived(Math.floor(skill.total_practice_minutes / 60));
	const mins = $derived(skill.total_practice_minutes % 60);
</script>

<a
	href="/skills/{skill.id}"
	class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent/50"
>
	<span class="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/10">
		<Brain class="h-4 w-4 text-purple-500" />
	</span>
	<div class="min-w-0 flex-1">
		<p class="truncate font-medium">{skill.name}</p>
		<p class="text-xs text-muted-foreground">
			{skill.due_count} sub-skill{skill.due_count !== 1 ? 's' : ''} due
			&middot;
			{#if hours > 0}{hours}h {/if}{mins}m practiced
		</p>
	</div>
	<span
		class="inline-flex items-center rounded-full bg-purple-500/10 px-2 py-0.5 text-xs font-medium text-purple-600"
	>
		{skill.category}
	</span>
</a>
