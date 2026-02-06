<script lang="ts">
	import '../app.css';
	import { Toaster } from '$lib/components/ui/sonner';

	let { children } = $props();
</script>

<svelte:head>
	<title>Trainer</title>
	<meta name="description" content="Unified training and habit tracking" />
</svelte:head>

<Toaster />
{@render children()}
