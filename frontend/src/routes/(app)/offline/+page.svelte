<script lang="ts">
	import WifiOff from '@lucide/svelte/icons/wifi-off';
	import { onMount } from 'svelte';
	import { getQueueSize } from '$lib/offline-queue';

	let queueSize = $state(0);

	onMount(async () => {
		try {
			queueSize = await getQueueSize();
		} catch {
			// IndexedDB may not be available
		}
	});
</script>

<div class="flex min-h-[60vh] flex-col items-center justify-center text-center">
	<WifiOff class="mb-4 h-12 w-12 text-muted-foreground opacity-50" />
	<h1 class="mb-2 text-xl font-bold">You're offline</h1>
	<p class="mb-4 text-sm text-muted-foreground">
		Check your internet connection and try again.
	</p>
	{#if queueSize > 0}
		<p class="text-sm text-muted-foreground">
			{queueSize} change{queueSize !== 1 ? 's' : ''} queued — will sync when you reconnect.
		</p>
	{/if}
</div>
