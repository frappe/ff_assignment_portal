<template>
    <div class="m-4">
        <h1 class=" font-bold mb-2 text-gray-600">SQL Portal</h1>
        <LoadingText v-if="problemSet.loading" />
        <div v-else-if="problemSet.doc">
            <div class="prose prose-md" v-html="md2html(problemSet.doc.introduction)"></div>
        </div>

        <hr>

        <ol class="mt-10" v-for="problem, index in problems" :key="problem.name">
            <li>
                <span class="font-semibold text-gray-600 underline underline-offset-1">Problem {{ index + 1 }}</span>
                <SQLProblem :problem="problem" />
            </li>
        </ol>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { md2html } from '@/utils';
import { useRoute } from 'vue-router';
import { sessionUser } from '@/data/session'
import SQLProblem from '@/components/sql/SQLProblem.vue';
import { createDocumentResource, LoadingText, createListResource} from 'frappe-ui';

const route = useRoute();
const problems = ref([]);

const problemSet = createDocumentResource({
    doctype: "SQL Problem Set",
    name: route.params.psetName,
    auto: true,
    onSuccess(d) {
        const problemNames = d.problems.map((p) => p.problem)
        createListResource({
            doctype: "SQL Problem",
            fields: ["name", "problem_statement"],
            filters: {
                "name": ["in", problemNames]
            },
            onSuccess(d) {
                problems.value = d;
            },
            auto: true
        })

        createListResource({
            doctype: "SQL Problem Solution",
            fields: ["status", "name", "last_submitted_query"],
            filters: {
                student: sessionUser()
            },
            auto:true,
            onSuccess(d) {
                console.log(d)
            }
        })

    }
})
</script>
