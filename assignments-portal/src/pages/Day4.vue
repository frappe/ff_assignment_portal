<template>
  <div class="max-w-3xl mb-10">
    <Alert
      >Note: This assignment will be <strong>graded manually</strong> and feedback will be given
      during the evaluation call</Alert
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
