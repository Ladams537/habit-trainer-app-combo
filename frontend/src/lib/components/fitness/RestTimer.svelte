<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import X from '@lucide/svelte/icons/x';

	let {
		duration = 120,
		onclose
	}: {
		duration?: number;
		onclose: () => void;
	} = $props();

	let remaining = $state(duration);
	let intervalId: ReturnType<typeof setInterval> | null = null;

	$effect(() => {
		remaining = duration;
		intervalId = setInterval(() => {
			remaining -= 1;
			if (remaining <= 0) {
				onclose();
			}
		}, 1000);

		return () => {
			if (intervalId) clearInterval(intervalId);
		};
	});

	const minutes = $derived(Math.floor(remaining / 60));
	const seconds = $derived(remaining % 60);
	const progress = $derived(((duration - remaining) / duration) * 100);
</script>

<div
	class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm"
>
	<div class="w-72 rounded-2xl border border-border bg-card p-8 text-center shadow-lg">
		<p class="mb-2 text-sm font-medium text-muted-foreground">Rest Timer</p>

		<div class="relative mx-auto mb-6 h-36 w-36">
			<svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
				<circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="4" class="text-muted/20" />
				<circle
					cx="50"
					cy="50"
					r="45"
					fill="none"
					stroke="currentColor"
					stroke-width="4"
					stroke-dasharray={2 * Math.PI * 45}
					stroke-dashoffset={2 * Math.PI * 45 * (1 - progress / 100)}
					stroke-linecap="round"
					class="text-primary transition-all duration-1000"
				/>
			</svg>
			<div class="absolute inset-0 flex items-center justify-center">
				<span class="text-3xl font-bold tabular-nums">
					{minutes}:{seconds.toString().padStart(2, '0')}
				</span>
			</div>
		</div>

		<Button variant="outline" onclick={onclose} class="w-full">
			<X class="mr-1 h-4 w-4" />
			Skip
		</Button>
	</div>
</div>
