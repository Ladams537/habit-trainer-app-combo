<script lang="ts">
	import type { CalendarDay, CalendarEvent } from '$lib/api/analytics';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { Button } from '$lib/components/ui/button';

	interface Props {
		days: CalendarDay[];
		currentMonth: number;
		currentYear: number;
		onNavigate: (year: number, month: number) => void;
	}

	let { days, currentMonth, currentYear, onNavigate }: Props = $props();

	let selectedDate = $state<string | null>(null);

	const monthName = $derived(
		new Date(currentYear, currentMonth - 1).toLocaleDateString('en-GB', {
			month: 'long',
			year: 'numeric'
		})
	);

	const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

	const daysByDate = $derived(() => {
		const map = new Map<string, CalendarDay>();
		for (const day of days) {
			map.set(day.date, day);
		}
		return map;
	});

	const calendarGrid = $derived(() => {
		const firstDay = new Date(currentYear, currentMonth - 1, 1);
		const lastDay = new Date(currentYear, currentMonth, 0);
		const startDow = (firstDay.getDay() + 6) % 7; // Monday = 0
		const totalDays = lastDay.getDate();

		const cells: { day: number | null; dateStr: string | null }[] = [];

		// Leading blanks
		for (let i = 0; i < startDow; i++) {
			cells.push({ day: null, dateStr: null });
		}

		// Actual days
		for (let d = 1; d <= totalDays; d++) {
			const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
			cells.push({ day: d, dateStr });
		}

		return cells;
	});

	const selectedDayEvents = $derived(() => {
		if (!selectedDate) return [];
		const map = daysByDate();
		const day = map.get(selectedDate);
		return day?.events ?? [];
	});

	function prevMonth() {
		let m = currentMonth - 1;
		let y = currentYear;
		if (m < 1) {
			m = 12;
			y--;
		}
		onNavigate(y, m);
	}

	function nextMonth() {
		let m = currentMonth + 1;
		let y = currentYear;
		if (m > 12) {
			m = 1;
			y++;
		}
		onNavigate(y, m);
	}

	function getDomainDots(dateStr: string): string[] {
		const map = daysByDate();
		const day = map.get(dateStr);
		if (!day) return [];
		const domains = new Set(day.events.map((e) => e.domain));
		const colors: string[] = [];
		if (domains.has('habits')) colors.push('#22C55E');
		if (domains.has('fitness')) colors.push('#3B82F6');
		if (domains.has('skills')) colors.push('#8B5CF6');
		return colors;
	}

	function getEventLink(event: CalendarEvent): string | null {
		if (event.domain === 'fitness' && event.event_type === 'workout') {
			return `/calendar/sessions/${event.entity_id}`;
		}
		if (event.domain === 'habits') {
			return `/habits/${event.entity_id}`;
		}
		if (event.domain === 'skills') {
			return `/skills/${event.entity_id}`;
		}
		if (event.domain === 'fitness' && event.event_type === 'program_active') {
			return `/programs/${event.entity_id}`;
		}
		return null;
	}

	const todayStr = new Date().toISOString().split('T')[0];
</script>

<div class="space-y-4">
	<!-- Month navigation -->
	<div class="flex items-center justify-between">
		<Button variant="ghost" size="sm" onclick={prevMonth}>
			<ChevronLeft class="h-4 w-4" />
		</Button>
		<h2 class="text-lg font-semibold">{monthName}</h2>
		<Button variant="ghost" size="sm" onclick={nextMonth}>
			<ChevronRight class="h-4 w-4" />
		</Button>
	</div>

	<!-- Day headers -->
	<div class="grid grid-cols-7 text-center text-xs font-medium text-muted-foreground">
		{#each daysOfWeek as dow}
			<div class="py-1">{dow}</div>
		{/each}
	</div>

	<!-- Calendar grid -->
	<div class="grid grid-cols-7 gap-px">
		{#each calendarGrid() as cell}
			{#if cell.day === null}
				<div class="h-12"></div>
			{:else}
				{@const dots = getDomainDots(cell.dateStr!)}
				<button
					type="button"
					class="relative flex h-12 flex-col items-center justify-start rounded-md pt-1 text-sm transition-colors hover:bg-accent {selectedDate === cell.dateStr ? 'bg-accent ring-1 ring-primary' : ''} {cell.dateStr === todayStr ? 'font-bold' : ''}"
					onclick={() => (selectedDate = selectedDate === cell.dateStr ? null : cell.dateStr)}
				>
					<span class={cell.dateStr === todayStr ? 'text-primary' : ''}>{cell.day}</span>
					{#if dots.length > 0}
						<div class="mt-0.5 flex gap-0.5">
							{#each dots as color}
								<span
									class="inline-block h-1.5 w-1.5 rounded-full"
									style="background-color: {color}"
								></span>
							{/each}
						</div>
					{/if}
				</button>
			{/if}
		{/each}
	</div>

	<!-- Selected day events -->
	{#if selectedDate}
		<div class="space-y-2">
			<h3 class="text-sm font-medium text-muted-foreground">
				{new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-GB', {
					weekday: 'long',
					day: 'numeric',
					month: 'long'
				})}
			</h3>
			{#if selectedDayEvents().length === 0}
				<p class="text-sm text-muted-foreground">No activity on this day.</p>
			{:else}
				{#each selectedDayEvents() as event}
					{@const link = getEventLink(event)}
					{#if link}
						<a
							href={link}
							class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:bg-accent"
						>
							<span
								class="inline-block h-2.5 w-2.5 rounded-full"
								style="background-color: {event.color || '#6B7280'}"
							></span>
							<div class="flex-1 min-w-0">
								<div class="font-medium text-sm">{event.title}</div>
								{#if event.subtitle}
									<div class="text-xs text-muted-foreground">{event.subtitle}</div>
								{/if}
							</div>
							<ChevronRight class="h-4 w-4 text-muted-foreground" />
						</a>
					{:else}
						<div class="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
							<span
								class="inline-block h-2.5 w-2.5 rounded-full"
								style="background-color: {event.color || '#6B7280'}"
							></span>
							<div class="flex-1 min-w-0">
								<div class="font-medium text-sm">{event.title}</div>
								{#if event.subtitle}
									<div class="text-xs text-muted-foreground">{event.subtitle}</div>
								{/if}
							</div>
						</div>
					{/if}
				{/each}
			{/if}
		</div>
	{/if}
</div>
