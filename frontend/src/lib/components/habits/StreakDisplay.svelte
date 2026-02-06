<script lang="ts">
	import Flame from '@lucide/svelte/icons/flame';

	let { streak = 0, strength = 0 }: { streak?: number; strength?: number } = $props();

	const strengthLabel = $derived(
		strength >= 0.75 ? 'Rooted' : strength >= 0.5 ? 'Strong' : strength >= 0.25 ? 'Growing' : 'Weak'
	);

	const strengthPercent = $derived(Math.round(strength * 100));
</script>

<div class="flex items-center gap-3 text-sm">
	{#if streak > 0}
		<div class="flex items-center gap-1 text-orange-500">
			<Flame class="h-4 w-4" />
			<span class="font-medium">{streak}</span>
		</div>
	{/if}
	{#if strength > 0}
		<div class="flex items-center gap-1.5">
			<div class="h-1.5 w-12 overflow-hidden rounded-full bg-muted">
				<div
					class="h-full rounded-full transition-all duration-500"
					style="width: {strengthPercent}%; background-color: var(--color-habits)"
				></div>
			</div>
			<span class="text-xs text-muted-foreground">{strengthLabel}</span>
		</div>
	{/if}
</div>
