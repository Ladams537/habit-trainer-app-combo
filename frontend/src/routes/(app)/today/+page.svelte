<script lang="ts">
	import { enhance } from '$app/forms';
	import HabitChecklist from '$lib/components/habits/HabitChecklist.svelte';
	import SkillCard from '$lib/components/skills/SkillCard.svelte';
	import { Button } from '$lib/components/ui/button';
	import Plus from '@lucide/svelte/icons/plus';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import Play from '@lucide/svelte/icons/play';
	import Brain from '@lucide/svelte/icons/brain';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	let { data } = $props();

	let selectedTemplateId = $state('');

	const today = new Date().toLocaleDateString('en-GB', {
		weekday: 'long',
		day: 'numeric',
		month: 'long'
	});

	const completedSets = $derived(
		data.activeSession?.exercise_groups.reduce(
			(sum, g) => sum + g.sets.filter((s) => s.completed).length,
			0
		) ?? 0
	);

	const exerciseCount = $derived(data.activeSession?.exercise_groups.length ?? 0);
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

	<!-- Workout Card -->
	<div class="rounded-lg border border-border bg-card p-4">
		<div class="mb-3 flex items-center gap-2">
			<span
				class="inline-block h-3 w-3 rounded-full"
				style="background-color: var(--color-fitness, #3B82F6)"
			></span>
			<h2 class="text-lg font-semibold">Workout</h2>
		</div>

		{#if data.activeSession}
			<div class="space-y-3">
				<div class="text-sm text-muted-foreground">
					{data.activeSession.template_name || 'Free-form workout'} in progress
				</div>
				<div class="flex items-center gap-4 text-sm">
					<span>{exerciseCount} exercise{exerciseCount !== 1 ? 's' : ''}</span>
					<span>{completedSets} set{completedSets !== 1 ? 's' : ''} logged</span>
				</div>
				<Button href="/workout" class="w-full">
					<Dumbbell class="mr-1 h-4 w-4" />
					Resume Workout
				</Button>
			</div>
		{:else}
			<div class="space-y-3">
				{#if data.activeProgram}
					<Button href="/programs/{data.activeProgram.id}" class="w-full" variant="default">
						<Dumbbell class="mr-1 h-4 w-4" />
						Continue Program: {data.activeProgram.name}
						{#if data.activeProgram.current_week}
							— Week {data.activeProgram.current_week}
						{/if}
						<ChevronRight class="ml-auto h-4 w-4" />
					</Button>
				{/if}
				<form method="POST" action="?/startWorkout" use:enhance class="space-y-3">
					{#if data.templates.length > 0}
						<select
							name="templateId"
							bind:value={selectedTemplateId}
							class="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
						>
							<option value="">Free-form (no template)</option>
							{#each data.templates as template}
								<option value={template.id}>
									{template.name} ({template.exercises.length} exercises)
								</option>
							{/each}
						</select>
					{/if}
					<Button type="submit" class="w-full" variant={data.activeProgram ? 'outline' : 'default'}>
						<Play class="mr-1 h-4 w-4" />
						Start Workout
					</Button>
				</form>
			</div>
		{/if}
	</div>

	<!-- Skills Card -->
	{#if data.skillsDue.length > 0}
		<div class="rounded-lg border border-border bg-card p-4">
			<div class="mb-3 flex items-center gap-2">
				<span
					class="inline-block h-3 w-3 rounded-full"
					style="background-color: #8B5CF6"
				></span>
				<h2 class="text-lg font-semibold">Skills to Practice</h2>
			</div>
			<div class="space-y-2">
				{#each data.skillsDue as skill (skill.id)}
					<SkillCard {skill} />
				{/each}
			</div>
		</div>
	{/if}

	<HabitChecklist habits={data.habits} />
</div>
