<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	let { form } = $props();

	const colors = ['#22c55e', '#3b82f6', '#f97316', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];
	let selectedColor = $state('#22c55e');
	let habitType = $state('boolean');
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold">New habit</h1>

	<Card.Root>
		<Card.Content class="pt-6">
			<form method="POST" use:enhance class="space-y-4">
				{#if form?.error}
					<div class="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
						{form.error}
					</div>
				{/if}

				<div class="space-y-2">
					<Label for="name">Name</Label>
					<Input id="name" name="name" required placeholder="e.g. Drink water, Read, Meditate" />
				</div>

				<div class="space-y-2">
					<Label for="habit_type">Type</Label>
					<select
						id="habit_type"
						name="habit_type"
						bind:value={habitType}
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
					>
						<option value="boolean">Yes/No (check off)</option>
						<option value="numeric">Numeric (track a count)</option>
						<option value="duration">Duration (track time)</option>
					</select>
				</div>

				{#if habitType !== 'boolean'}
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-2">
							<Label for="target_value">Target</Label>
							<Input id="target_value" name="target_value" type="number" min="1" value="1" />
						</div>
						<div class="space-y-2">
							<Label for="unit">Unit</Label>
							<Input
								id="unit"
								name="unit"
								placeholder={habitType === 'duration' ? 'minutes' : 'glasses'}
							/>
						</div>
					</div>
				{/if}

				<div class="space-y-2">
					<Label for="frequency">Frequency</Label>
					<select
						id="frequency"
						name="frequency"
						class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
					>
						<option value="daily">Every day</option>
						<option value="weekdays">Weekdays only</option>
					</select>
				</div>

				<div class="space-y-2">
					<Label>Color</Label>
					<input type="hidden" name="color" value={selectedColor} />
					<div class="flex gap-2">
						{#each colors as color}
							<button
								type="button"
								onclick={() => (selectedColor = color)}
								class="h-8 w-8 rounded-full border-2 transition-all {selectedColor === color
									? 'border-foreground scale-110'
									: 'border-transparent'}"
								style="background-color: {color}"
							></button>
						{/each}
					</div>
				</div>

				<div class="flex gap-3 pt-2">
					<Button type="submit" class="flex-1">Create habit</Button>
					<Button href="/today" variant="outline">Cancel</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>
</div>
