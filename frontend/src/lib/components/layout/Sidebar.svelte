<script lang="ts">
	import { page } from '$app/state';
	import Brain from '@lucide/svelte/icons/brain';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import ChartLine from '@lucide/svelte/icons/chart-line';
	import Dumbbell from '@lucide/svelte/icons/dumbbell';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import LogOut from '@lucide/svelte/icons/log-out';

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

<aside class="fixed left-0 top-0 hidden h-full w-60 flex-col border-r border-border bg-sidebar md:flex">
	<div class="flex items-center gap-2 border-b border-border px-4 py-4">
		<Dumbbell class="h-6 w-6 text-primary" />
		<span class="text-lg font-semibold">Trainer</span>
	</div>

	<nav class="flex flex-1 flex-col gap-1 p-3">
		{#each navItems as item}
			<a
				href={item.href}
				class="flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors {isActive(item.href)
					? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
					: 'text-sidebar-foreground hover:bg-sidebar-accent/50'}"
			>
				<item.icon class="h-4 w-4" />
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="border-t border-border p-3">
		<form method="POST" action="/logout">
			<button
				type="submit"
				class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent/50"
			>
				<LogOut class="h-4 w-4" />
				<span>Sign out</span>
			</button>
		</form>
	</div>
</aside>
