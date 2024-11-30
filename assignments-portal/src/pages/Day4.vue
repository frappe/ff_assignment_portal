<template>
  <div class="max-w-3xl mb-10">
    <div>
      <p></p>
    </div>
    <Alert
      >Note: This assignment will be only be <strong>graded manually for candidates who have opted for certification</strong> and feedback will be given
      during the evaluation call. Please don't wait for this assignment's result and schedule your evaluation call from the batch dashboard page.</Alert
    >
  </div>

  <AssignmentArea
    day="4"
    :assignment-summary="props.assignmentSummary"
    :assignment-summary-resource="props.assignmentSummaryResource"
    @submitted="displayEvaluationDialog"
  />

  <Dialog v-model="showEvalDialog" :options="{
    title: 'Evaluation Time!',
    message: 'Now that you have submitted your final assignment, it is time to schedule your evaluation call with us. Feedback for this assignment will be given during the same call. You can do that from the batch dashboard of your enrolled batch.',
    actions: [
      {
        label: 'View Batches',
        variant: 'solid',
        link: 'https://frappe.school/lms/batches'
      }
    ]
  }" />

</template>

<script setup>
import { ref } from 'vue'
import AssignmentArea from '../components/AssignmentArea.vue'
import { Alert, Dialog } from 'frappe-ui'

const showEvalDialog = ref(false);

const props = defineProps({
  assignmentSummary: {
    type: Object,
    required: true,
  },
  assignmentSummaryResource: {
    type: Object,
    required: true,
  },
})

function displayEvaluationDialog() {
  setTimeout(() => showEvalDialog.value = true, 900);
}
</script>
