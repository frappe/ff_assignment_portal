<template>
  <div>
    <div v-if="!props.assignmentSummary[`day-${props.day}`]">
      <h1 class="font-black text-gray-900 text-2xl">Day {{ props.day }}</h1>
      <h2 class="font-medium text-gray-800 text-lg mt-6">Submission Area</h2>

      <div class="mt-4">
        <p class="mt-2 text-sm text-gray-500">
          Upload your submission here. It should be a zip file containing your
          JSON files.
        </p>

        <div class="mt-4 flex flex-row space-x-3">
          <FileUploader
            @error="handleUploadError"
            @success="handleUploadSuccess"
            :upload-args="{
              upload_endpoint:
                '/api/method/ff_assignment_portal.api.upload_assignment_submission',
            }"
          >
            <template v-slot="{ uploading, openFileSelector, error }">
              <Button @click="openFileSelector" :loading="uploading"
                >Attach Solution Zip</Button
              >

              <ErrorMessage class="mt-2" :message="error" />
            </template>
          </FileUploader>

          <Button
            @loading="submitAssignment.isLoading"
            :disabled="!selectedFileDoc"
            @click="handleAssignmentSubmit"
            variant="solid"
            size="sm"
            >Submit</Button
          >
        </div>
      </div>

      <p v-if="selectedFileDoc" class="mt-2 text-sm text-gray-500">
        Selected File: {{ selectedFileDoc.file_name }}
      </p>
      <p v-else class="mt-2 text-sm text-gray-500">No File Selected</p>

      <ErrorMessage class="mt-2" :message="submitAssignment.error" />
    </div>

    <div class="mt-6">
      <h2 class="font-semibold text-gray-900">Submissions</h2>

      <div class="mt-4">
        <div v-if="assignmentSubmissions.isLoading">
          <Spinner />
        </div>

        <div v-else-if="!assignmentSubmissions.data?.length">
          <p class="text-sm text-gray-500">No submissions yet.</p>
        </div>

        <div class="sm:grid sm:grid-cols-2 gap-2" v-else>
          <div v-for="submission in submissions" :key="submission.name">
            <div class="border p-3 space-y-3 rounded-sm h-full shadow-sm">
              <div>
                <div class="flex items-start justify-between">
                  <div>
                    <h3
                      v-if="submission.status != 'Check In Progress'"
                      class="font-medium text-gray-600 text-xs mb-1"
                    >
                      Result
                    </h3>
                    <Badge
                      variant="outline"
                      :theme="statusColorMap[submission.status] || 'gray'"
                      >{{ submission.status }}</Badge
                    >
                  </div>

                  <div>
                    <p class="text-xs text-gray-600">
                      {{ submission.creation }}
                    </p>
                  </div>
                </div>

                <h3
                  v-if="submission.status == 'Check In Progress'"
                  class="font-medium text-gray-600 text-xs mt-3"
                >
                  You will be notified when the check is complete.
                </h3>
              </div>

              <div v-if="submission.feedback">
                <h3 class="font-medium text-gray-600 text-xs mb-1">Feedback</h3>
                <div class="text-base" v-html="submission.feedback" />
              </div>

              <div v-if="submission.submission_summary">
                <h3 class="font-medium text-gray-600 text-xs mb-1">Summary</h3>
                <div class="text-base" v-html="submission.submission_summary" />
              </div>
            </div>
          </div>
        </div>
        <!-- <div class="mx-2" v-else>
          <ListView
            :columns="[
              {
                label: 'Submitted On',
                key: 'creation',
                width: '200px'
              },
              {
                label: 'Status',
                key: 'status',
                width: '200px',
              },
              {
                label: 'Feedback',
                key: 'feedback',
                width: '400px',
              },
              {
                label: 'Summary',
                key: 'submission_summary',
              },
            ]"
            :rows="submissions"
            :options="{
              showTooltip: false,
              selectable: false,
            }"
            row-key="id"
          />
        </div> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  FileUploader,
  Badge,
  createListResource,
  Spinner,
  createResource,
  ErrorMessage,
  ListView,
} from 'frappe-ui'
import dayjs from 'dayjs'

import { computed, ref } from 'vue'
import { sessionUser } from '../../src/data/session'

const props = defineProps({
  day: {
    type: String,
    required: true,
  },
  assignmentSummary: {
    type: Object,
    required: true,
  },
  assignmentSummaryResource: {
    type: Object,
    required: true,
  },
})

const statusColorMap = {
  Failed: 'red',
  Passed: 'green',
  'Check In Progress': 'blue',
  Stale: 'gray',
}

const selectedFileDoc = ref(null)

function handleUploadSuccess(file) {
  selectedFileDoc.value = file
}

function handleUploadError(error) {
  console.error(error)
}

const submitAssignment = createResource({
  url: '/api/method/ff_assignment_portal.ff_assignment_portal.doctype.ff_assignment_submission.ff_assignment_submission.submit_assignment',
  onSuccess() {
    selectedFileDoc.value = null
    assignmentSubmissions.reload()
    props.assignmentSummaryResource.reload()
  },
})

function handleAssignmentSubmit() {
  submitAssignment.submit({
    day: props.day,
    file: selectedFileDoc.value,
  })
}

const assignmentSubmissions = createListResource({
  doctype: 'FF Assignment Submission',
  fields: ['name', 'feedback', 'status', 'creation', 'submission_summary'],
  filters: {
    user: sessionUser(),
    day: props.day,
  },
  orderBy: 'creation desc',
  auto: true,
  realtime: true,
})

const submissions = computed(() => {
  if (!assignmentSubmissions.data) return []

  return assignmentSubmissions.data.map((submission) => {
    return {
      ...submission,
      creation: dayjs(submission.creation).format('hh:mm A | DD MMMM YYYY'),
      feedback: submission.feedback ? submission.feedback : '-',
    }
  })
})
</script>
