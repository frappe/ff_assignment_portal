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
  />

</template>

<script setup>
import AssignmentArea from '../components/AssignmentArea.vue'
import { Alert } from 'frappe-ui'

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
</script>
