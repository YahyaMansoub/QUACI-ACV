<template>
  <div class="space-details">
    <h2>{{ space.name }}</h2>
    <p>Facteurs : {{ space.factors }}</p>

    <h3>Maisons ({{ space.houses.length }})</h3>
    <LoadingSpinner v-if="loading" />
    <div v-else class="houses-list">
      <HouseCard
        v-for="house in space.houses"
        :key="house.id"
        :house="house"
      />
    </div>
  </div>
</template>

<script>
import HouseCard from './HouseCard.vue'
import LoadingSpinner from './LoadingSpinner.vue'

export default {
  name: 'SpaceDetails',
  components: { HouseCard, LoadingSpinner },
  props: ['spaceId'],
  data() {
    return {
      space: { name: '', factors: '', houses: [] },
      loading: true
    }
  },
  created() {
    fetch(`/api/spaces/${this.spaceId}`)
      .then(res => res.json())
      .then(data => {
        this.space = data
      })
      .catch(err => console.error(err))
      .finally(() => this.loading = false)
  }
}
</script>

<style scoped>
.space-details {
  padding: 20px;
}
.houses-list {
  display: flex;
  flex-wrap: wrap;
}
</style>