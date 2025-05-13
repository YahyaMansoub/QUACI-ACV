<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFile = ref(null)
const message = ref('')
const error = ref('')
const results = ref({})

function onFileChange(event) {
  selectedFile.value = event.target.files[0]
  message.value = ''
  error.value = ''
  results.value = {}
}

async function submitFile() {
  if (!selectedFile.value) {
    error.value = 'Please select a CSV file to upload.'
    return
  }
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.value = response.data.message || 'File uploaded successfully.'
    error.value = ''
    await fetchAllResults()
  } catch (err) {
    error.value = err.response?.data?.error || 'Upload failed.'
    message.value = ''
  }
}

async function fetchAllResults() {
  const methods = ['discernability', 'heijungs', 'ranking', 'heatmap']
  results.value = {}
  for (const method of methods) {
    try {
      const res = await axios.get(`/api/upload/results/${method}`)
      results.value[method] = res.data[method]
    } catch (err) {
      console.warn(`Failed to fetch result for ${method}:`, err.response?.data?.error || err.message)
    }
  }
}
</script>

<template>
  <div class="csv-uploader p-4 border rounded shadow-md max-w-md mx-auto">
    <h3 class="text-lg font-semibold mb-4">Upload CSV File</h3>
    <form @submit.prevent="submitFile">
      <input type="file" @change="onFileChange" accept=".csv" class="mb-4" />
      <button
        type="submit"
        :disabled="!selectedFile"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        Upload & Analyze
      </button>
    </form>
    <p v-if="message" class="mt-2 text-green-600">{{ message }}</p>
    <p v-if="error" class="mt-2 text-red-600">{{ error }}</p>

    <!-- Show simple preview of result keys -->
    <div v-if="Object.keys(results).length" class="mt-4">
      <h4 class="font-semibold mb-2">Available Results:</h4>
      <ul class="list-disc list-inside text-sm">
        <li v-for="(value, key) in results" :key="key">{{ key }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.csv-uploader {
  background-color: #f9fafb;
}
</style>
