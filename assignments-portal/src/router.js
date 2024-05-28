import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

// /assignments-portal/framework/day-1
// /assignments-portal/sql/pset-0

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/framework/day-1',
  },
  {
    path: '/framework',
    component: () => import("@/pages/FrameworkPortal.vue"),
    children: [
      {
        path: 'day-1',
        name: 'Day1',
        component: () => import('@/pages/Day1.vue'),
      },
      {
        path: 'day-2',
        name: 'Day2',
        component: () => import('@/pages/Day2.vue'),
      },
      {
        path: 'day-3',
        name: 'Day3',
        component: () => import('@/pages/Day3.vue'),
      },
      {
        path: 'day-4',
        name: 'Day4',
        component: () => import('@/pages/Day4.vue'),
      },
    ]
  },
  {
    path: '/sql/:psetName',
    name: 'SQL Portal',
    component: () => import("@/pages/SQLPortal.vue")
  }
]

let router = createRouter({
  history: createWebHistory('/assignments-portal'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    window.location.href = `/login?redirect-to=/assignments-portal${to.path}`
  } else {
    next()
  }
})

export default router
