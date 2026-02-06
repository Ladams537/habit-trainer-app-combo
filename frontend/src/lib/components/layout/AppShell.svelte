<script lang="ts">
	import BottomNav from './BottomNav.svelte';
	import Sidebar from './Sidebar.svelte';

	let { children } = $props();
</script>

<div class="min-h-screen bg-background">
	<Sidebar />

	<!-- Main content: offset for sidebar on desktop, padding for bottom nav on mobile -->
	<main class="pb-20 md:ml-60 md:pb-0">
		<div class="mx-auto max-w-4xl px-4 py-6">
			{@render children()}
		</div>
	</main>

	<BottomNav />
</div>
