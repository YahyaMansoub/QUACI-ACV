import { createRouter, createWebHistory } from 'vue-router'
import DashBoard from '../views/DashBoard.vue'  // Verify component import
import SpaceDetails from '../views/SpaceDetails.vue'

const routes = [
  {
    path: '/',
    name: 'DashBoard',
    component: DashBoard  // Ensure correct component name
  },
  {
    path: '/spaces/:spaceId',
    name: 'SpaceDetails',
    component: SpaceDetails,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

