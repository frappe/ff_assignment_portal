<template>
  <div>
    <h1 class="font-black text-gray-900 text-2xl">Day {{ props.day }} Assignment</h1>
    <div v-if="!props.assignmentSummary[`day-${props.day}`]">
      <h2 class="font-medium text-gray-800 text-lg mt-6">Submission Area</h2>

      <div class="mt-4">
        <p class="mt-2 text-sm text-gray-500">
          Upload your submission here. It should be a zip file containing your
          JSON files.
        </p>

        <div class="mt-4 flex flex-row space-x-3">
          <FileUploader
            @error="handleUploadError"
            @success="(file) => handleUploadSuccess('assignment', file)"
            :fileTypes="['application/zip']"
          >
            <template v-slot="{ uploading, openFileSelector, error, progress }">
              <Button @click="openFileSelector" :loading="uploading"
                >Attach Solution Zip</Button
              >
              <p class="text-sm text-gray-500 mt-2 block" v-if="uploading">{{ progress }}% uploaded</p>
              <ErrorMessage class="mt-2" :message="error" />
            </template>
          </FileUploader>

        
          <FileUploader
            v-if="props.day == 4"
            @error="handleUploadError"
            @success="(file) => handleUploadSuccess('demo_video', file)"
            :fileTypes="['video/*']"
          >
            <template v-slot="{ uploading, openFileSelector, error, progress }">
              <Button @click="openFileSelector" :loading="uploading"
                >Attach Demo Video</Button
              >
              <p class="text-sm text-gray-500 mt-2 block" v-if="uploading">{{ progress }}% uploaded</p>
              <p class="text-sm text-gray-500 mt-2 block" v-else>Only video files allowed upto 300MB allowed.</p>
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

      <div class="mt-4 flex flex-col gap-2">
        <p class="mt-2 text-sm text-gray-600"><strong>Selected Assignment File: </strong>
          <span  v-if="selectedFileDoc">
            <CheckCircleIcon class="w-4 text-green-700 inline"/>
            {{ selectedFileDoc.file_name }}
          </span>
          <span v-else>
            <ExclamationCircleIcon class="w-4 text-amber-600 inline" />
            No File Selected</span>
        </p>

        <p v-if="props.day == 4" class="mt-2 text-sm text-gray-600"><strong>Selected Demo File: </strong>
          <span  v-if="selectedDemoVideo">
            <CheckCircleIcon class="w-4 text-green-700 inline"/>
            {{ selectedDemoVideo.file_name }}
          </span>
          <span v-else>
            <ExclamationCircleIcon class="w-4 text-amber-600 inline" />
            No File Selected
          </span>
        </p>
      </div>

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
        <div>
          <!-- LATER -->
  <!-- <ListView
    class="h-[250px]"
    :columns="listColumns"
    :rows="[
      {
        id: 1,
        name: 'John Doe',
        email: 'john@doe.com',
        status: 'Active',
        role: 'Developer',
        user_image: 'https://avatars.githubusercontent.com/u/499550',
      },
      {
        id: 2,
        name: 'Jane Doe',
        email: 'jane@doe.com',
        status: 'Inactive',
        role: 'HR',
        user_image: 'https://avatars.githubusercontent.com/u/499120',
      },
    ]"
    :options="listOptions"
    row-key="id"
  >
    <template #cell="{ item, row, column }">
      <span class="font-medium text-gray-700">
        {{ row }} - {{ column }}
      </span>
    </template>
  </ListView> -->
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
  ListView,
} from 'frappe-ui'
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/solid'
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

const emit = defineEmits(['submitted']);

const statusColorMap = {
  Failed: 'red',
  Passed: 'green',
  'Check In Progress': 'blue',
  Stale: 'gray',
}

const selectedFileDoc = ref(null)
const selectedDemoVideo = ref(null)

function handleUploadSuccess(uploadType, file) {
  if (uploadType === 'demo_video') {
    selectedDemoVideo.value = file
    
  } else {
    selectedFileDoc.value = file
  }

}

function handleUploadError(error) {
  console.error(error)
}

const submitAssignment = createResource({
  url: '/api/method/ff_assignment_portal.ff_assignment_portal.doctype.ff_assignment_submission.ff_assignment_submission.submit_assignment',
  onSuccess() {
    selectedFileDoc.value = null
    selectedDemoVideo.value = null
    assignmentSubmissions.reload()
    props.assignmentSummaryResource.reload()
    emit('submitted');
  },
})

function handleAssignmentSubmit() {
  console.log({
    day: props.day,
    file: selectedFileDoc.value,
    demo_video: selectedDemoVideo.value,
  })
  submitAssignment.submit({
    day: props.day,
    file: selectedFileDoc.value,
    demo_video: selectedDemoVideo.value,
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
