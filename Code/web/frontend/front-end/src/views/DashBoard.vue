<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <!-- House Selection -->
    <div class="mb-6">
      <label for="house-select" class="block text-sm font-medium text-gray-700 mb-1">Select House</label>
      <select
        id="house-select"
        v-model="selectedHouse"
        class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="" disabled>Select a house</option>
        <option v-for="house in houses" :key="house.id" :value="house.id">
          {{ house.name }}
        </option>
      </select>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading.data" class="flex justify-center items-center h-64">
      <span class="text-gray-500 text-lg">Loading...</span>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <!-- Total Environmental Impact -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Total Environmental Impact</h3>
          <ul class="space-y-2">
            <li v-for="(value, key) in envImpact" :key="key" class="text-gray-600">
              <span class="font-medium text-gray-700">{{ key }}:</span> {{ formatNumber(value) }}
            </li>
          </ul>
        </div>

        <!-- Materials Weight -->
        <div class="bg-white shadow rounded-lg p-6 overflow-auto max-h-96 col-span-full lg:col-span-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Materials Weight</h3>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Weight</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="mat in materials" :key="mat.name">
                <td class="px-4 py-2 text-gray-700">{{ mat.name }}</td>
                <td class="px-4 py-2 text-gray-700">{{ formatNumber(mat.weight) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Charts and Visualizations -->
      <div class="space-y-8">
        <section v-if="discernOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">Discernibility Matrix</h3>
          <vue-echarts :option="discernOption" class="h-64" />
        </section>

        <section v-if="smdOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">SMD Heatmap</h3>
          <vue-echarts :option="smdOption" class="h-64" />
        </section>

        <section v-if="drdOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">DRD Heatmap</h3>
          <vue-echarts :option="drdOption" class="h-64" />
        </section>

        <section v-if="drdBoxOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">DRD Boxplot</h3>
          <vue-echarts :option="drdBoxOption" class="h-64" />
        </section>

        <section v-if="heijungsOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">Heijungs Significance</h3>
          <vue-echarts :option="heijungsOption" class="h-64" />
        </section>

        <section v-if="rankingOption">
          <h3 class="text-xl font-semibold text-gray-800 mb-4">Ranking Probabilities</h3>
          <vue-echarts :option="rankingOption" class="h-64" />
        </section>
      </div>

      <!-- Download Button -->
      <div class="mt-6">
        <button
          @click="downloadCSV"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Download Matrix CSV
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()

const houses = computed(() => store.houses)
const loading = computed(() => store.loading)
const envImpact = computed(() => store.envImpact || {})
const materials = computed(() => store.materials || [])
const smd = computed(() => store.smd)
const drd = computed(() => store.drd)
const discern = computed(() => store.discern)
const heijungs = computed(() => store.heijungs)
const ranking = computed(() => store.ranking)

const selectedHouse = ref('')

onMounted(() => {
  store.fetchHouses()
})

watch(selectedHouse, (id) => {
  if (id) store.selectHouse(id)
})

function formatNumber(val) {
  return Number(val).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function buildHeatmapOption(matrix) {
  if (!matrix || !matrix.rows) return {}
  return {
    tooltip: { position: 'top' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: matrix.cols },
    yAxis: { type: 'category', data: matrix.rows },
    visualMap: {
      min: 0,
      max: Math.max(...matrix.data.map(item => item[2])),
      calculable: true
    },
    series: [{
      name: 'heatmap',
      type: 'heatmap',
      data: matrix.data,
      emphasis: {
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        }
      }
    }]
  }
}

function buildBoxplotOption(matrix) {
  if (!matrix || !matrix.boxData) return {}
  return {
    tooltip: { trigger: 'item' },
    xAxis: { type: 'category', data: matrix.axis },
    yAxis: {},
    series: [{
      name: 'boxplot',
      type: 'boxplot',
      data: matrix.boxData,
      tooltip: {
        formatter: params =>
          `Min: ${params.data[0]}<br/>Q1: ${params.data[1]}<br/>Median: ${params.data[2]}<br/>Q3: ${params.data[3]}<br/>Max: ${params.data[4]}`
      }
    }]
  }
}

function buildBarOption(data, labelKey = 'category', valueKey = 'value') {
  if (!data) return {}
  return {
    xAxis: { type: 'category', data: data.map(d => d[labelKey]) },
    yAxis: {},
    series: [{
      type: 'bar',
      data: data.map(d => d[valueKey])
    }]
  }
}

const discernOption = computed(() => buildHeatmapOption(discern.value))
const smdOption = computed(() => buildHeatmapOption(smd.value))
const drdOption = computed(() => buildHeatmapOption(drd.value))
const drdBoxOption = computed(() => buildBoxplotOption(drd.value))
const heijungsOption = computed(() => buildBarOption(heijungs.value, 'metric', 'significance'))
const rankingOption = computed(() => buildBarOption(ranking.value, 'item', 'probability'))

function downloadCSV() {
  if (!store.uncertainty) return
  const matrix = store.uncertainty.matrix || []
  const header = store.uncertainty.cols.join(',')
  const rows = matrix.map(r => r.join(','))
  const csv = [header, ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.setAttribute('download', `impact-matrix-${selectedHouse.value}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>


<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  position: relative;
}

.spaces-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.spaces-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.space-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  width: 250px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #4CAF50;
}

.space-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.space-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.factors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
}

.factors span {
  background: #e0f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #00838f;
}

.add-space-btn {
  position: fixed;
  right: 30px;
  top: 30px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 25px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-space-btn:hover {
  background: #388E3C;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.add-space-btn span {
  font-size: 20px;
  font-weight: bold;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.space-form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.space-form h3 {
  margin-top: 0;
  color: #2c3e50;
}

.form-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.factors-input {
  margin-bottom: 20px;
}

.factor-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.factor-item input {
  flex: 1;
}

.remove-factor {
  background: #ff5252;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-factor {
  background: none;
  border: 1px dashed #4CAF50;
  color: #4CAF50;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.add-factor:hover {
  background: #e8f5e9;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.submit-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

/* Animation */
.space-fade-enter-active,
.space-fade-leave-active {
  transition: all 0.5s ease;
}

.space-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.space-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
