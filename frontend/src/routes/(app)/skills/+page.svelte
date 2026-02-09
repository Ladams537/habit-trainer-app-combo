<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import Brain from '@lucide/svelte/icons/brain';
	import Plus from '@lucide/svelte/icons/plus';

	let { data } = $props();
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Skills</h1>
		<Button href="/skills/new" size="sm">
			<Plus class="mr-1 h-4 w-4" />
			New skill
		</Button>
	</div>

	{#if data.skills.length === 0}
		<Card.Root>
			<Card.Content class="py-8 text-center text-muted-foreground">
				No skills yet. Add your first skill to start tracking your practice.
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="space-y-2">
			{#each data.skills as skill (skill.id)}
				<a
					href="/skills/{skill.id}"
					class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent/50"
				>
					<span
						class="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/10"
					>
						<Brain class="h-4 w-4 text-purple-500" />
					</span>
					<div class="min-w-0 flex-1">
						<p class="truncate font-medium">{skill.name}</p>
						<p class="text-xs text-muted-foreground">
							{skill.category} &middot; {skill.sub_skills.length} sub-skill{skill.sub_skills
								.length !== 1
								? 's'
								: ''}
						</p>
					</div>
					<span class="text-xs text-muted-foreground capitalize">{skill.current_level}</span>
				</a>
			{/each}
		</div>
	{/if}
</div>
