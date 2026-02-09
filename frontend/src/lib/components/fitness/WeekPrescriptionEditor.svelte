<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import type { ProgramDayPrescription } from '$lib/api/programs';

	let {
		prescriptions = $bindable([]),
		readonly = false
	}: {
		prescriptions: ProgramDayPrescription[];
		readonly?: boolean;
	} = $props();

	function updateExercise(dayIdx: number, exIdx: number, field: string, value: number) {
		prescriptions = prescriptions.map((day, di) => {
			if (di !== dayIdx) return day;
			return {
				...day,
				exercises: day.exercises.map((ex, ei) => {
					if (ei !== exIdx) return ex;
					return { ...ex, [field]: value };
				})
			};
		});
	}
</script>

<div class="space-y-4">
	{#each prescriptions as day, dayIdx (dayIdx)}
		<Card.Root>
			<Card.Header class="pb-2">
				<Card.Title class="text-base">{day.day_label}</Card.Title>
			</Card.Header>
			<Card.Content class="space-y-3">
				{#if day.exercises.length === 0}
					<p class="text-sm text-muted-foreground">No exercises assigned</p>
				{/if}
				{#each day.exercises as exercise, exIdx (exIdx)}
					<div class="rounded-md border border-border p-3 space-y-2">
						<div class="font-medium text-sm">{exercise.exercise_name}</div>
						{#if readonly}
							<div class="grid grid-cols-4 gap-2 text-xs text-muted-foreground">
								<div><span class="font-medium text-foreground">{exercise.sets}</span> sets</div>
								<div><span class="font-medium text-foreground">{exercise.reps}</span> reps</div>
								<div><span class="font-medium text-foreground">{exercise.weight_kg}</span>kg</div>
								<div><span class="font-medium text-foreground">{exercise.rest_seconds}</span>s rest</div>
							</div>
						{:else}
							<div class="grid grid-cols-4 gap-2">
								<div class="space-y-1">
									<Label class="text-xs">Sets</Label>
									<Input
										type="number"
										min="1"
										value={exercise.sets}
										oninput={(e) => updateExercise(dayIdx, exIdx, 'sets', parseInt(e.currentTarget.value) || 1)}
										class="h-8 text-xs"
									/>
								</div>
								<div class="space-y-1">
									<Label class="text-xs">Reps</Label>
									<Input
										type="number"
										min="1"
										value={exercise.reps}
										oninput={(e) => updateExercise(dayIdx, exIdx, 'reps', parseInt(e.currentTarget.value) || 1)}
										class="h-8 text-xs"
									/>
								</div>
								<div class="space-y-1">
									<Label class="text-xs">Weight</Label>
									<Input
										type="number"
										min="0"
										step="0.5"
										value={exercise.weight_kg}
										oninput={(e) => updateExercise(dayIdx, exIdx, 'weight_kg', parseFloat(e.currentTarget.value) || 0)}
										class="h-8 text-xs"
									/>
								</div>
								<div class="space-y-1">
									<Label class="text-xs">Rest(s)</Label>
									<Input
										type="number"
										min="0"
										step="15"
										value={exercise.rest_seconds}
										oninput={(e) => updateExercise(dayIdx, exIdx, 'rest_seconds', parseInt(e.currentTarget.value) || 60)}
										class="h-8 text-xs"
									/>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</Card.Content>
		</Card.Root>
	{/each}
</div>
