<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Plus from '@lucide/svelte/icons/plus';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Pencil from '@lucide/svelte/icons/pencil';

	let { data } = $props();
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<Button href="/programs" variant="ghost" size="sm">
			<ArrowLeft class="h-4 w-4" />
		</Button>
		<h1 class="flex-1 text-2xl font-bold">Templates</h1>
		<Button href="/programs/templates/new" variant="outline" size="sm">
			<Plus class="mr-1 h-4 w-4" />
			New Template
		</Button>
	</div>

	{#if data.templates.length === 0}
		<div class="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
			<Dumbbell class="mx-auto mb-3 h-10 w-10 opacity-40" />
			<p class="mb-2 font-medium">No templates yet</p>
			<p class="text-sm">Templates are exercise lists used to build program days.</p>
			<Button href="/programs/templates/new" variant="default" size="sm" class="mt-4">
				<Plus class="mr-1 h-4 w-4" />
				Create Template
			</Button>
		</div>
	{:else}
		<div class="space-y-3">
			{#each data.templates as template (template.id)}
				<div class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
					<div class="flex-1 min-w-0">
						<div class="font-medium">{template.name}</div>
						<div class="text-sm text-muted-foreground">
							{template.exercises.length} exercise{template.exercises.length !== 1 ? 's' : ''}
							{#if template.description}
								· {template.description}
							{/if}
						</div>
					</div>
					<div class="flex items-center gap-1">
						<Button href="/programs/templates/{template.id}" variant="ghost" size="sm">
							<Pencil class="h-4 w-4" />
						</Button>
						<form method="POST" action="?/deleteTemplate" use:enhance={() => {
							return async ({ update }) => { await update(); };
						}}>
							<input type="hidden" name="templateId" value={template.id} />
							<Button type="submit" variant="ghost" size="sm">
								<Trash2 class="h-4 w-4 text-destructive" />
							</Button>
						</form>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
