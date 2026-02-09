<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import type { ProgressionOption, ProgramDayPrescription } from '$lib/api/programs';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import Minus from '@lucide/svelte/icons/minus';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';

	let {
		options,
		currentPrescriptions,
		programId,
		weekNum
	}: {
		options: ProgressionOption[];
		currentPrescriptions: ProgramDayPrescription[];
		programId: string;
		weekNum: number;
	} = $props();

	const optionIcons: Record<string, typeof TrendingUp> = {
		conservative: Minus,
		standard: TrendingUp,
		aggressive: ArrowUp
	};

	const optionColors: Record<string, string> = {
		conservative: 'border-blue-500/30 hover:border-blue-500',
		standard: 'border-green-500/30 hover:border-green-500',
		aggressive: 'border-orange-500/30 hover:border-orange-500'
	};

	function getWeightDiff(optionExercises: ProgramDayPrescription[], dayIdx: number, exIdx: number): string {
		const current = currentPrescriptions[dayIdx]?.exercises[exIdx];
		const next = optionExercises[dayIdx]?.exercises[exIdx];
		if (!current || !next) return '';
		const diff = next.weight_kg - current.weight_kg;
		if (diff === 0) return '';
		return diff > 0 ? `+${diff.toFixed(1)}kg` : `${diff.toFixed(1)}kg`;
	}
</script>

<div class="grid gap-3 md:grid-cols-3">
	{#each options as option (option.key)}
		{@const Icon = optionIcons[option.key] || TrendingUp}
		<Card.Root class="transition-colors {optionColors[option.key] || ''}">
			<Card.Header class="pb-2">
				<Card.Title class="flex items-center gap-2 text-base">
					<Icon class="h-4 w-4" />
					{option.label}
				</Card.Title>
				<p class="text-xs text-muted-foreground">{option.description}</p>
			</Card.Header>
			<Card.Content class="space-y-2">
				{#each option.prescriptions as day, dayIdx}
					<div class="text-xs">
						<div class="font-medium">{day.day_label}</div>
						{#each day.exercises as ex, exIdx}
							{@const diff = getWeightDiff(option.prescriptions, dayIdx, exIdx)}
							<div class="text-muted-foreground flex items-center gap-1">
								<span>{ex.exercise_name}: {ex.sets}x{ex.reps} @ {ex.weight_kg}kg</span>
								{#if diff}
									<span class="font-medium {diff.startsWith('+') ? 'text-green-500' : 'text-red-500'}">{diff}</span>
								{/if}
							</div>
						{/each}
					</div>
				{/each}

				<form method="POST" action="/programs/{programId}/week/{weekNum}?/acceptProgression" use:enhance>
					<input type="hidden" name="option_key" value={option.key} />
					<Button type="submit" variant="outline" size="sm" class="w-full mt-2">
						Choose {option.label}
					</Button>
				</form>
			</Card.Content>
		</Card.Root>
	{/each}
</div>
