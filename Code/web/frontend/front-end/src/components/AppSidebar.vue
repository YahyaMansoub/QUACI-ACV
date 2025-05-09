<template>
  <aside :class="['bg-white shadow-md transition-all duration-300 h-screen', visible ? 'w-64' : 'w-16']">
    <div class="h-full flex flex-col">
      <div class="p-4 font-semibold text-gray-700 border-b" v-if="visible">
        Navigation
      </div>
      <ul class="p-4 space-y-2">
        <li>
          <router-link
            to="/dashboard"
            class="flex items-center gap-2 px-4 py-2 rounded hover:bg-blue-100 transition"
            :class="{ 'bg-blue-100 text-blue-800 font-bold': $route.path === '/dashboard' }"
          >
            📊 <span v-if="visible">Dashboard</span>
          </router-link>
        </li>
        <li>
          <router-link
            to="/spaces"
            class="flex items-center gap-2 px-4 py-2 rounded hover:bg-blue-100 transition"
            :class="{ 'bg-blue-100 text-blue-800 font-bold': $route.path === '/spaces' }"
          >
            🏡 <span v-if="visible">Spaces</span>
          </router-link>
        </li>
        <!-- Add more navigation items as needed -->
      </ul>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AppSidebar',
  props: {
    visible: { type: Boolean, default: true }
  }
}
</script>


<style scoped>
aside {
  transition: width 0.3s ease;
}

.router-link-active {
  font-weight: bold;
  color: #1e40af; /* Tailwind's blue-800 */
}

.router-link-active:hover {
  background-color: #bfdbfe; /* Tailwind's blue-100 */
}
</style>