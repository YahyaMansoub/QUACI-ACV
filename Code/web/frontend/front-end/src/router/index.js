import { createRouter, createWebHistory } from 'vue-router'
import DashBoard from '../views/DashBoard.vue'  // Keep this import

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashBoard
  },
  {
    path: '/spaces/:spaceId',
    name: 'SpaceDetails',
    component: () => import('../views/SpaceDetails.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
