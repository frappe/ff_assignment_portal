<template>
	<div class="m-4">
		<h1 class="mb-1 font-semibold text-gray-600">SQL Practice Portal</h1>
		<LoadingText v-if="problemSet.loading" />
		<div class="mb-2" v-else-if="problemSet.doc">
			<div class="prose prose-md prose-h1:text-gray-800" v-html="md2html(problemSet.doc.introduction)"></div>
		</div>

		<hr>

		<ol class="mt-10" v-for="problem, index in problems" :key="problem.name">
			<li class="max-w-2xl mx-auto">
				<SQLProblem :index="index" :problem="problem" />
			</li>
		</ol>
	</div>
</template>

<script setup>
import { computed, watch, ref } from 'vue';
import { md2html } from '@/utils';
import { useRoute } from 'vue-router';
import SQLProblem from '@/components/sql/SQLProblem.vue';
import { createDocumentResource, LoadingText, createListResource} from 'frappe-ui';

const route = useRoute();
const problems = ref([]);

const problemSet = createDocumentResource({
	doctype: "SQL Problem Set",
	name: route.params.psetName,
	auto: true
})

const problemsInThisSet = computed(() => {
	const d = problemSet.doc;
	if (d) {
		return d.problems.map((p) => p.problem);
	}

	return [];
})

watch(problemsInThisSet, () => {
	createListResource({
		doctype: "SQL Problem",
		fields: ["name", "problem_statement"],
		filters: {
			"name": ["in", problemsInThisSet.value]
		},
		onSuccess(d) {
			problems.value = d;
		},
		auto: true
	})
})
</script>
