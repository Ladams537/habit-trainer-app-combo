<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';

	let { data, form } = $props();

	let name = $state('');
	let description = $state('');
	let workoutsPerWeek = $state(3);
	let selectedTemplateIds = $state<string[]>([]);

	function addTemplate(id: string) {
		if (selectedTemplateIds.length < workoutsPerWeek) {
			selectedTemplateIds = [...selectedTemplateIds, id];
		}
	}

	function removeTemplate(index: number) {
		selectedTemplateIds = selectedTemplateIds.filter((_, i) => i !== index);
	}

	const availableTemplates = $derived(
		data.templates.filter((t) => true)
	);

	const selectedTemplates = $derived(
		selectedTemplateIds.map((id) => data.templates.find((t) => t.id === id)).filter(Boolean)
	);
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/programs" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<h1 class="text-2xl font-bold">New Program</h1>
	</div>

	<Card.Root>
		<Card.Content class="pt-6">
			<form method="POST" use:enhance class="space-y-4">
				{#if form?.error}
					<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
						{form.error}
					</div>
				{/if}

				<div class="space-y-2">
					<Label for="name">Program Name</Label>
					<Input id="name" name="name" bind:value={name} required placeholder="e.g. PPL Strength Block" />
				</div>

				<div class="space-y-2">
					<Label for="description">Description (optional)</Label>
					<Input id="description" name="description" bind:value={description} placeholder="8-week hypertrophy focus" />
				</div>

				<div class="space-y-2">
					<Label for="workouts_per_week">Workouts per week</Label>
					<select
						id="workouts_per_week"
						name="workouts_per_week"
						bind:value={workoutsPerWeek}
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
					>
						{#each [1, 2, 3, 4, 5, 6, 7] as n}
							<option value={n}>{n}x per week</option>
						{/each}
					</select>
				</div>

				<div class="space-y-2">
					<Label>Day Templates ({selectedTemplateIds.length}/{workoutsPerWeek})</Label>
					<p class="text-xs text-muted-foreground">Assign a template to each workout day. You'll set weights in Week 1.</p>

					{#if selectedTemplates.length > 0}
						<div class="space-y-2">
							{#each selectedTemplates as template, i}
								{#if template}
									<div class="flex items-center gap-2 rounded-md border border-border px-3 py-2">
										<span class="text-xs font-medium text-muted-foreground">Day {i + 1}</span>
										<span class="flex-1 text-sm">{template.name}</span>
										<button type="button" onclick={() => removeTemplate(i)} class="text-muted-foreground hover:text-foreground">
											<X class="h-4 w-4" />
										</button>
									</div>
								{/if}
							{/each}
						</div>
					{/if}

					{#if selectedTemplateIds.length < workoutsPerWeek && availableTemplates.length > 0}
						<div class="flex flex-wrap gap-2 pt-1">
							{#each availableTemplates as template (template.id)}
								<button
									type="button"
									onclick={() => addTemplate(template.id)}
									class="flex items-center gap-1 rounded-full border border-border px-3 py-1 text-xs transition-colors hover:bg-accent"
								>
									<Plus class="h-3 w-3" />
									{template.name}
								</button>
							{/each}
						</div>
					{/if}
				</div>

				<input type="hidden" name="template_ids" value={JSON.stringify(selectedTemplateIds)} />

				<div class="flex gap-3 pt-2">
					<Button type="submit" class="flex-1" disabled={!name}>Create Program</Button>
					<Button href="/programs" variant="outline">Cancel</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>
</div>
