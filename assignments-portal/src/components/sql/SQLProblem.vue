<template>
    <div>
                <div class="mt-3" v-html="md2html(problem.problem_statement)"></div>
                <div class="mt-1 flex flex-row items-end space-x-1 max-w-lg">
                    <FormControl
                        :type="'textarea'"
                        size="sm"
                        class="w-80"
                        variant="subtle"
                        placeholder="Your query"
                        label="Solution"
                        v-model="solution"
                    />
    
                <Button @click="(e) => handleSolutionSubmit(e)">Submit</Button>
        </div>
    </div>
</template>

<script setup>
import { md2html } from '@/utils';
import { ref, reactive } from 'vue';
import confetti from 'canvas-confetti';
import { FormControl, Button, createResource } from 'frappe-ui';

const solution = ref("");
const confettiPosition = reactive({x: 0.5, y: 0.5});

const props = defineProps({
    problem: {
        type: Object,
        required: true
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

