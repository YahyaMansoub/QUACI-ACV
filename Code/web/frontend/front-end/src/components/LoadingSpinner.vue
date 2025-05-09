<template>
  <div class="spinner"></div>
</template>

<script>
export default {
  name: 'LoadingSpinner'
}
</script>

<style scoped>
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: #35495e;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>