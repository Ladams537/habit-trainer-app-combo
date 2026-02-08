<script lang="ts">
	import { page } from '$app/state';
	import Brain from '@lucide/svelte/icons/brain';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import ChartLine from '@lucide/svelte/icons/chart-line';
	import ListChecks from '@lucide/svelte/icons/list-checks';

	const navItems = [
		{ href: '/today', label: 'Today', icon: ListChecks },
		{ href: '/plan', label: 'Plan', icon: CalendarDays },
		{ href: '/skills', label: 'Skills', icon: Brain },
		{ href: '/analytics', label: 'Analytics', icon: ChartLine }
	];

	function isActive(href: string): boolean {
		return page.url.pathname.startsWith(href);
	}
</script>

<nav class="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-background pb-[env(safe-area-inset-bottom)] md:hidden">
	<div class="flex items-center justify-around">
		{#each navItems as item}
			<a
				href={item.href}
				class="flex flex-1 flex-col items-center gap-1 py-3 text-xs transition-colors {isActive(item.href)
					? 'text-primary'
					: 'text-muted-foreground hover:text-foreground'}"
			>
				<item.icon class="h-5 w-5" />
				<span>{item.label}</span>
			</a>
		{/each}
	</div>
</nav>
