<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import SubSkillList from '$lib/components/skills/SubSkillList.svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Brain from '@lucide/svelte/icons/brain';
	import Clock from '@lucide/svelte/icons/clock';
	import Target from '@lucide/svelte/icons/target';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Play from '@lucide/svelte/icons/play';

	let { data } = $props();

	const skill = $derived(data.progress.skill);
	const hours = $derived(Math.floor(skill.total_practice_minutes / 60));
	const mins = $derived(skill.total_practice_minutes % 60);
	const dueCount = $derived(data.schedule.schedule.filter((s) => s.is_due).length);
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/skills" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<div class="flex-1">
			<div class="flex items-center gap-2">
				<span
					class="flex h-6 w-6 items-center justify-center rounded-full bg-purple-500/10"
				>
					<Brain class="h-3 w-3 text-purple-500" />
				</span>
				<h1 class="text-2xl font-bold">{skill.name}</h1>
			</div>
			<p class="text-sm text-muted-foreground capitalize">{skill.category} &middot; {skill.current_level}</p>
		</div>
	</div>

	<!-- Stats cards -->
	<div class="grid grid-cols-3 gap-3">
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<Clock class="mb-1 h-5 w-5 text-purple-500" />
				<span class="text-2xl font-bold">
					{#if hours > 0}{hours}h{/if}{mins}m
				</span>
				<span class="text-xs text-muted-foreground">Practice</span>
			</Card.Content>
		</Card.Root>
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<Target class="mb-1 h-5 w-5 text-purple-500" />
				<span class="text-2xl font-bold">{dueCount}</span>
				<span class="text-xs text-muted-foreground">Due</span>
			</Card.Content>
		</Card.Root>
		<Card.Root>
			<Card.Content class="flex flex-col items-center py-4">
				<Brain class="mb-1 h-5 w-5 text-purple-500" />
				<span class="text-2xl font-bold">{data.progress.competency_levels.length}</span>
				<span class="text-xs text-muted-foreground">Sub-skills</span>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Practice button -->
	<Button href="/skills/{skill.id}/practice" class="w-full bg-purple-600 hover:bg-purple-700">
		<Play class="mr-1 h-4 w-4" />
		Start Practice
	</Button>

	<!-- Sub-skills with FSRS data -->
	{#if data.progress.competency_levels.length > 0}
		<Card.Root>
			<Card.Header>
				<Card.Title>Sub-skills</Card.Title>
			</Card.Header>
			<Card.Content>
				<SubSkillList levels={data.progress.competency_levels} />
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Recent practice sessions -->
	<Card.Root>
		<Card.Header>
			<Card.Title>Recent practice</Card.Title>
		</Card.Header>
		<Card.Content>
			{#if data.progress.recent_sessions.length === 0}
				<p class="text-sm text-muted-foreground">No practice sessions yet.</p>
			{:else}
				<div class="space-y-2">
					{#each data.progress.recent_sessions as session}
						<div class="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
							<div>
								<span class="font-medium">{session.duration_minutes}min</span>
								{#if session.focus_area}
									<span class="text-muted-foreground"> &middot; {session.focus_area}</span>
								{/if}
							</div>
							<div class="flex items-center gap-2 text-muted-foreground">
								<span class="text-purple-500">{'★'.repeat(session.quality_rating)}{'☆'.repeat(5 - session.quality_rating)}</span>
								<span class="text-xs">{new Date(session.practiced_at).toLocaleDateString()}</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>

	<!-- Archive -->
	<Card.Root class="border-destructive/50">
		<Card.Content class="flex items-center justify-between py-4">
			<div>
				<p class="font-medium">Archive skill</p>
				<p class="text-sm text-muted-foreground">Hides from view, keeps all history</p>
			</div>
			<form method="POST" action="?/delete" use:enhance>
				<Button type="submit" variant="destructive" size="sm">
					<Trash2 class="mr-1 h-4 w-4" />
					Archive
				</Button>
			</form>
		</Card.Content>
	</Card.Root>
</div>
