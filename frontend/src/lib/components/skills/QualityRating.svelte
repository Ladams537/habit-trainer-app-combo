<script lang="ts">
	import Star from '@lucide/svelte/icons/star';

	let {
		value = $bindable(0),
	}: {
		value: number;
	} = $props();

	let hoverValue = $state(0);

	const labels = ['', 'Again', 'Hard', 'Okay', 'Good', 'Easy'];
</script>

<div class="space-y-1">
	<div class="flex items-center gap-1">
		{#each [1, 2, 3, 4, 5] as rating}
			<button
				type="button"
				class="rounded p-1 transition-colors hover:bg-accent"
				onmouseenter={() => (hoverValue = rating)}
				onmouseleave={() => (hoverValue = 0)}
				onclick={() => (value = rating)}
			>
				<Star
					class="h-7 w-7 transition-colors {(hoverValue || value) >= rating
						? 'fill-purple-500 text-purple-500'
						: 'text-muted-foreground/40'}"
				/>
			</button>
		{/each}
	</div>
	{#if hoverValue || value}
		<p class="text-sm text-muted-foreground">{labels[hoverValue || value]}</p>
	{/if}
</div>
