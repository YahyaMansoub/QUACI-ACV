<template>
  <div class="layout">
    <AppSidebar :visible="sidebarVisible" />

    <div class="main-content">
      <NavBar @toggle-sidebar="toggleSidebar" :title="title" />

      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import AppSidebar from './AppSidebar.vue'
import NavBar from './NavBar.vue'

export default {
  name: 'Layout',
  components: {
    AppSidebar,
    NavBar
  },
  data() {
    return {
      sidebarVisible: true,
      title: 'QUACI-ACV'
    }
  },
  methods: {
    toggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible
    }
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: #f9fafb;
  color: #1f2937;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.content-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background-color: #ffffff;
}
</style>
