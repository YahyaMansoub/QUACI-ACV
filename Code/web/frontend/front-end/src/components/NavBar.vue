<template>
  <header class="bg-blue-900 text-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <!-- Left: Toggle Button -->
        <div class="flex items-center">
          <button
            @click="$emit('toggle-sidebar')"
            class="text-white hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-white"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2"
                 viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <h1 class="ml-4 text-lg font-semibold">{{ title }}</h1>
        </div>

        <!-- Right: Navigation Links -->
        <nav class="hidden md:flex space-x-4">
          <router-link to="/" class="hover:text-blue-300">Dashboard</router-link>
          <router-link to="/spaces" class="hover:text-blue-300">Spaces</router-link>
          <div class="relative group">
            <button class="hover:text-blue-300 focus:outline-none">
              More
              <svg class="inline h-4 w-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.293l3.71-4.06a.75.75 0 111.08 1.04l-4.25 4.65a.75.75 0 01-1.08 0l-4.25-4.65a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
              </svg>
            </button>
            <div class="absolute right-0 mt-2 w-48 bg-white text-black rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50">
              <router-link to="/settings" class="block px-4 py-2 hover:bg-gray-100">Settings</router-link>
              <router-link to="/profile" class="block px-4 py-2 hover:bg-gray-100">Profile</router-link>
              <router-link to="/logout" class="block px-4 py-2 hover:bg-gray-100">Logout</router-link>
            </div>
          </div>
        </nav>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'NavBar',
  props: {
    title: { type: String, default: 'QUACI-ACV' }
  }
}
</script>
