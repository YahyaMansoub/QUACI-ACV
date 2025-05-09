<template>
  <div class="dashboard">
    <h2>Espaces</h2>
    <ul>
      <li v-for="space in spaces" :key="space.id">
        <router-link :to="{ name: 'SpaceDetails', params: { spaceId: space.id } }">
          {{ space.name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'DashBoard',
  data() {
    return { spaces: [] }
  },
  created() {
    fetch('/api/spaces')
      .then(res => res.json())
      .then(data => this.spaces = data)
      .catch(err => console.error(err))
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.dashboard ul {
  list-style: none;
  padding: 0;
}
.dashboard li {
  margin: 10px 0;
}
.dashboard a {
  color: #35495e;
  text-decoration: none;
}
.dashboard a:hover {
  text-decoration: underline;
}
</style>