<template>
    <AssignmentArea
      day="3"
      :assignment-summary="props.assignmentSummary"
      :assignment-summary-resource="props.assignmentSummaryResource"
    />
  </template>
  
  <script setup>
  import AssignmentArea from '../components/AssignmentArea.vue'
  
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
  