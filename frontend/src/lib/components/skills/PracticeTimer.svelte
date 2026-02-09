<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import Pause from '@lucide/svelte/icons/pause';
	import Play from '@lucide/svelte/icons/play';
	import Square from '@lucide/svelte/icons/square';

	let {
		onstop
	}: {
		onstop: (seconds: number) => void;
	} = $props();

	let elapsed = $state(0);
	let running = $state(false);
	let intervalId: ReturnType<typeof setInterval> | null = null;

	function start() {
		running = true;
		intervalId = setInterval(() => {
			elapsed += 1;
		}, 1000);
	}

	function pause() {
		running = false;
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}

	function stop() {
		pause();
		onstop(elapsed);
	}

	const minutes = $derived(Math.floor(elapsed / 60));
	const seconds = $derived(elapsed % 60);

	// Circular progress: full circle every 60 minutes
	const progress = $derived(Math.min((elapsed / 3600) * 100, 100));
</script>

<div class="flex flex-col items-center gap-6">
	<div class="relative mx-auto h-44 w-44">
		<svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
			<circle
				cx="50"
				cy="50"
				r="45"
				fill="none"
				stroke="currentColor"
				stroke-width="4"
				class="text-muted/20"
			/>
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
				class="text-purple-500 transition-all duration-1000"
			/>
		</svg>
		<div class="absolute inset-0 flex items-center justify-center">
			<span class="text-4xl font-bold tabular-nums">
				{minutes}:{seconds.toString().padStart(2, '0')}
			</span>
		</div>
	</div>

	<div class="flex gap-3">
		{#if !running}
			<Button onclick={start} size="lg">
				<Play class="mr-1 h-5 w-5" />
				{elapsed === 0 ? 'Start' : 'Resume'}
			</Button>
		{:else}
			<Button onclick={pause} variant="outline" size="lg">
				<Pause class="mr-1 h-5 w-5" />
				Pause
			</Button>
		{/if}

		{#if elapsed > 0}
			<Button onclick={stop} variant="secondary" size="lg">
				<Square class="mr-1 h-5 w-5" />
				Stop
			</Button>
		{/if}
	</div>
</div>
