<script lang="ts">
	import type { Exercise } from '$lib/api/fitness';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import Search from '@lucide/svelte/icons/search';
	import X from '@lucide/svelte/icons/x';

	let {
		exercises,
		onselect,
		onclose
	}: {
		exercises: Exercise[];
		onselect: (exercise: Exercise) => void;
		onclose?: () => void;
	} = $props();

	let search = $state('');
	let categoryFilter = $state('all');

	const categories = ['all', 'compound', 'isolation', 'cardio'];

	const muscleGroups = $derived(() => {
		const groups = new Set<string>();
		exercises.forEach((e) => e.muscle_groups.forEach((mg) => groups.add(mg)));
		return Array.from(groups).sort();
	});

	let muscleFilter = $state('all');

	const filtered = $derived(
		exercises.filter((e) => {
			if (search && !e.name.toLowerCase().includes(search.toLowerCase())) return false;
			if (categoryFilter !== 'all' && e.category !== categoryFilter) return false;
			if (muscleFilter !== 'all' && !e.muscle_groups.includes(muscleFilter)) return false;
			return true;
		})
	);
</script>

<div class="space-y-3">
	<div class="flex items-center gap-2">
		{#if onclose}
			<Button variant="ghost" size="sm" onclick={onclose}>
				<X class="h-4 w-4" />
			</Button>
		{/if}
		<div class="relative flex-1">
			<Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
			<Input
				type="text"
				placeholder="Search exercises..."
				bind:value={search}
				class="pl-9"
			/>
		</div>
	</div>

	<div class="flex gap-2 overflow-x-auto pb-1">
		{#each categories as cat}
			<button
				type="button"
				class="shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors {categoryFilter ===
				cat
					? 'bg-primary text-primary-foreground'
					: 'bg-muted text-muted-foreground hover:bg-accent'}"
				onclick={() => (categoryFilter = cat)}
			>
				{cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1)}
			</button>
		{/each}
	</div>

	<div class="flex gap-2 overflow-x-auto pb-1">
		<button
			type="button"
			class="shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors {muscleFilter ===
			'all'
				? 'bg-primary text-primary-foreground'
				: 'bg-muted text-muted-foreground hover:bg-accent'}"
			onclick={() => (muscleFilter = 'all')}
		>
			All muscles
		</button>
		{#each muscleGroups() as mg}
			<button
				type="button"
				class="shrink-0 rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors {muscleFilter ===
				mg
					? 'bg-primary text-primary-foreground'
					: 'bg-muted text-muted-foreground hover:bg-accent'}"
				onclick={() => (muscleFilter = mg)}
			>
				{mg}
			</button>
		{/each}
	</div>

	<div class="max-h-80 space-y-1 overflow-y-auto">
		{#each filtered as exercise (exercise.id)}
			<button
				type="button"
				class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-accent active:scale-[0.98]"
				onclick={() => onselect(exercise)}
			>
				<div>
					<div class="font-medium">{exercise.name}</div>
					<div class="text-xs text-muted-foreground">
						{exercise.category} · {exercise.muscle_groups.join(', ')}
						{#if exercise.equipment}· {exercise.equipment}{/if}
					</div>
				</div>
			</button>
		{:else}
			<div class="py-8 text-center text-sm text-muted-foreground">No exercises found.</div>
		{/each}
	</div>
</div>
