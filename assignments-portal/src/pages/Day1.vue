<template>
  <div>
    <div v-if="!props.assignmentSummary['day-1']">
      <h2 class="font-semibold text-gray-900">Submission Area</h2>

      <div class="mt-4">
        <p class="mt-2 text-sm text-gray-500">
          Upload your submission here. It should be a zip file containing your
          JSON files.
        </p>

        <div class="mt-4 flex flex-row space-x-3">
          <FileUploader
            @error="handleUploadError"
            @success="handleUploadSuccess"
          >
            <template v-slot="{ uploading, openFileSelector }">
              <Button @click="openFileSelector" :loading="uploading"
                >Attach Solution Zip</Button
              >
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

        <div v-else>
          <div
            v-for="submission in assignmentSubmissions.data"
            :key="submission.name"
          >
            <div class="border p-3 space-y-3 rounded-sm mb-2 shadow-sm">
              <div v-if="submission.feedback">
                <h3 class="font-medium text-gray-600 text-xs mb-1">Feedback</h3>
                <div class="text-base" v-html="submission.feedback" />
              </div>

              <div>
                <h3 class="font-medium text-gray-600 text-xs mb-1">Result</h3>
                <Badge
                  variant="outline"
                  :theme="
                    submission.status == 'Failed'
                      ? 'red'
                      : submission.status == 'Passed'
                      ? 'green'
                      : 'gray'
                  "
                  >{{ submission.status }}</Badge
                >
              </div>
            </div>
          </div>
        </div>
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
} from 'frappe-ui'
import { ref } from 'vue'
import { sessionUser } from '../../src/data/session'

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
    day: '1',
    file: selectedFileDoc.value,
  })
}

const assignmentSubmissions = createListResource({
  doctype: 'FF Assignment Submission',
  fields: ['name', 'feedback', 'status', 'creation'],
  filters: {
    user: sessionUser,
    day: '1',
  },
  orderBy: 'creation desc',
  auto: true,
  realtime: true,
})
</script>
