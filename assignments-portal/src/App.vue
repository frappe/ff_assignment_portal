<template>
  <nav aria-label="Progress">
    <div class="m-4" v-if="assignmentSummary.loading">
      <div class="flex flex-row space-x-2">
        <Spinner class="w-5 h-5" />
        <span>Loading...</span>
      </div>
    </div>

    <ol
      v-else
      role="list"
      class="divide-y divide-gray-300 rounded-md border border-gray-300 md:flex md:divide-y-0"
    >
      <li
        v-for="(step, stepIdx) in steps"
        :key="step.name"
        class="relative md:flex md:flex-1"
      >
        <RouterLink
          v-if="step.status === 'complete'"
          :to="step.href"
          class="group flex w-full items-center"
        >
          <span class="flex items-center px-6 py-4 text-sm font-medium">
            <span
              class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-green-600 group-hover:bg-green-800"
            >
              <CheckBadgeIcon class="h-6 w-6 text-white" aria-hidden="true" />
            </span>
            <span class="ml-4 text-sm font-medium text-gray-900">{{
              step.name
            }}</span>
          </span>
        </RouterLink>

        <RouterLink
          v-else-if="step.status === 'current'"
          :to="step.href"
          class="flex items-center px-6 py-4 text-sm font-medium"
          aria-current="step"
        >
          <span
            class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border-2 border-blue-600"
          >
            <span class="text-blue-600">{{ step.id }}</span>
          </span>
          <span class="ml-4 text-sm font-medium text-blue-600">{{
            step.name
          }}</span>
        </RouterLink>

        <RouterLink v-else :to="step.href" class="group flex items-center">
          <span class="flex items-center px-6 py-4 text-sm font-medium">
            <span
              class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border-2 border-gray-300 group-hover:border-gray-400"
            >
              <span class="text-gray-500 group-hover:text-gray-900">{{
                step.id
              }}</span>
            </span>
            <span
              class="ml-4 text-sm font-medium text-gray-500 group-hover:text-gray-900"
              >{{ step.name }}</span
            >
          </span>
        </RouterLink>

        <template v-if="stepIdx !== steps.length - 1">
          <!-- Arrow separator for lg screens and up -->
          <div
            class="absolute right-0 top-0 hidden h-full w-5 md:block"
            aria-hidden="true"
          >
            <svg
              class="h-full w-full text-gray-300"
              viewBox="0 0 22 80"
              fill="none"
              preserveAspectRatio="none"
            >
              <path
                d="M0 -2L20 40L0 82"
                vector-effect="non-scaling-stroke"
                stroke="currentcolor"
                stroke-linejoin="round"
              />
            </svg>
          </div>
        </template>
      </li>
    </ol>
  </nav>

  <div class="m-3" v-if="assignmentSummary.data">
    <router-view
      :assignmentSummary="assignmentSummary.data"
      :assignmentSummaryResource="assignmentSummary"
    />
  </div>
</template>

<script setup>
import { CheckBadgeIcon } from '@heroicons/vue/24/solid'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useRoute } from 'vue-router'
import { createResource, Spinner } from 'frappe-ui'

const route = useRoute()

const assignmentSummary = createResource({
  url: '/api/method/ff_assignment_portal.api.get_assignments_summary',
  auto: true,
})

const steps = computed(() => {
  if (!assignmentSummary.data) return []

  const currentPath = route.matched[0]?.path
  const status = (day) => {
    const path = `/${day}`
    if (assignmentSummary.data[day]) return 'complete'
    if (path === currentPath) return 'current'
    return 'upcoming'
  }

  return [
    { id: '01', name: 'Day 1', href: '/day-1', status: status('day-1') },
    { id: '02', name: 'Day 2', href: '/day-2', status: status('day-2') },
    { id: '03', name: 'Day 3', href: '/day-3', status: status('day-3') },
    { id: '04', name: 'Finals', href: '/day-4', status: status('day-4') },
  ]
})
</script>
