<template>
	<Card :title="`Problem #${props.index + 1}`">
		<div class="prose-sm" v-html="md2html(problem.problem_statement)"></div>
		<div class="flex flex-row space-x-3 mt-3 divide-x-2">	
			<div class="flex flex-col space-x-1 max-w-lg space-y-2">
				<FormControl
					:type="'textarea'"
					size="sm"
					class="w-96"
					variant="subtle"
					placeholder="Your query"
					label="Solution"
					v-model="solution"
					:disabled="status === 'Correct'"
				/>
	
			<Button  variant="outline" theme="blue" v-if="status !== 'Correct'" :loading="submitSolution.loading" @click="(e) => handleSolutionSubmit(e)">Submit</Button>
			<Badge class="shrink-0 w-fit" theme="green" v-else>Passed</Badge>
			</div>

			<div v-if="feedback" class="pl-3 max-w-lg">
				<h3 class=" font-semibold text-gray-600 text-sm">Feedback</h3>
				<div class="prose-sm" v-html="feedback"></div>
			</div>
		</div>
	</Card>
</template>

<script setup>
import { md2html } from '@/utils';
import { ref, reactive } from 'vue';
import confetti from 'canvas-confetti';
import { FormControl, Button, createResource, Badge, Card } from 'frappe-ui';

const solution = ref("");
const status = ref("Not Attempted");
const feedback = ref("");

const confettiPosition = reactive({x: 0.5, y: 0.5});

const props = defineProps({
	problem: {
		type: Object,
		required: true
	},
	index: {
		type: Number,
		default: 1
	}
})

const solutionResource = createResource({
	url: "ff_assignment_portal.api.get_solution_status",
	params: {
		problem: props.problem.name
	},
	auto: true,
	onSuccess(d) {
		status.value = d.status;

		if (d.status != "Not Attempted") {
			solution.value = d.last_submitted_query;
			feedback.value = d.feedback;
		} 
	}
})

const submitSolution = createResource({
	url: "ff_assignment_portal.api.submit_sql_solution",
	onSuccess(d) {
		if (d.status === "Correct") {
			confetti({
				particleCount: 100,
				spread: 70,
				origin: {x: confettiPosition.x, y: confettiPosition.y}
			});
		}

		solutionResource.reload()
	}
})

function handleSolutionSubmit(e) {
	confettiPosition.x = e.x / window.innerWidth;
	confettiPosition.y = e.y / window.innerHeight;

	submitSolution.submit({
		problem: props.problem.name,
		solution: solution.value
	})
}
</script>

