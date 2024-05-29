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
                <div class="mt-3" v-html="md2html(problem.problem_statement)"></div>

                <div class="mt-1 flex flex-row items-end space-x-1 max-w-lg">
                    <FormControl
                        :type="'textarea'"
                        size="sm"
                        class="w-80"
                        variant="subtle"
                        placeholder="Your query"
                        label="Solution"
                        v-model="solutions[problem.name]"
                    />
    
                    <Button @click="(e) => handleSolutionSubmit(e, problem.name)">Submit</Button>
                </div>

            </li>
        </ol>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import markdownit from 'markdown-it'
import { useRoute } from 'vue-router';
import { sessionUser } from '../../src/data/session'
import { createDocumentResource, LoadingText, createListResource, FormControl, Button, createResource } from 'frappe-ui';

import confetti from 'canvas-confetti';

window.c = confetti

const route = useRoute();
const problems = ref([]);
const solutions = reactive({});
const confettiPosition = reactive({x: 0.5, y: 0.5});

const md = markdownit();

function md2html(markdown) {
    return md.render(markdown);
}

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
            fields: "*",
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

const submitSolution = createResource({
    url: "/api/method/ff_assignment_portal.api.submit_sql_solution",
    onSuccess(d) {
        if (d.status === "Correct") {
                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: {x: confettiPosition.x, y: confettiPosition.y}
                });
            }

    }
})

function handleSolutionSubmit(e, problem) {
    confettiPosition.x = e.x / window.innerWidth;
    confettiPosition.y = e.y / window.innerHeight;

    submitSolution.submit({
        problem,
        solution: solutions[problem]
    })
}

</script>
