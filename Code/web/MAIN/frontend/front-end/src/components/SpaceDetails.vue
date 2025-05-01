<template>
  <div class="space-details">
    <!-- Upload Houses -->
    <div class="upload-section">
      <h2>Upload Houses (CSV)</h2>
      <form @submit.prevent="uploadHouse">
        <input type="file" ref="houseFile" accept=".csv" required />
        <input type="text" v-model="newHouseName" placeholder="Optional House Name" />
        <button type="submit" class="upload-btn">Upload CSV</button>
      </form>
    </div>

    <!-- Display Houses -->
    <div class="houses-list" v-if="houses.length">
      <h2>Uploaded Houses</h2>
      <ul>
        <li 
          v-for="house in houses" 
          :key="house.id" 
          @click="toggleHouseSelection(house.id)" 
          :class="{ selected: selectedHouses.includes(house.id) }"
        >
          {{ house.name }} — {{ house.simulations }} simulations
        </li>
      </ul>
    </div>

    <!-- Analysis Controls -->
    <div class="analysis-controls">
      <div class="selection-info">
        Selected Houses: {{ selectedHouses.length }}
        <button 
          @click="runDiscernabilityAnalysis" 
          :disabled="selectedHouses.length < 2"
          class="analyze-btn"
        >
          Run Discernability Analysis
        </button>
      </div>
    </div>

    <!-- Enhanced Heatmap Display -->
    <div v-if="heatmapData" class="heatmap-container">
      <div class="heatmap-wrapper">
        <!-- Factors Header -->
        <div class="factors-header">
          <div class="empty-cell"></div>
          <div 
            v-for="(factor, fidx) in space.factors" 
            :key="fidx"
            class="factor-header"
            :style="{ width: cellSize + 'px' }"
          >
            {{ factor }}
          </div>
        </div>

        <transition-group name="heatmap-row" tag="div" class="heatmap-body">
          <div 
            v-for="(comparison, cidx) in comparisons" 
            :key="cidx"
            class="comparison-row"
          >
            <div class="comparison-label">
              {{ getHouseName(comparison.house1) }} vs {{ getHouseName(comparison.house2) }}
            </div>
            
            <transition-group name="heatmap-cell" tag="div" class="factors-row">
              <div
                v-for="(value, fidx) in comparison.values"
                :key="fidx"
                class="factor-cell"
                :style="{
                  width: cellSize + 'px',
                  height: cellSize + 'px',
                  backgroundColor: getColor(value),
                  animationDelay: fidx * 0.05 + 's'
                }"
                @mouseenter="showTooltip($event, comparison, fidx, value)"
                @mouseleave="activeTooltip = null"
              >
                <span class="cell-value">{{ value.toFixed(2) }}</span>
              </div>
            </transition-group>
          </div>
        </transition-group>
      </div>

      <div v-if="activeTooltip" class="heatmap-tooltip" :style="tooltipStyle">
        <div class="tooltip-header">
          {{ activeTooltip.comparison }}
        </div>
        <div class="tooltip-body">
          <strong>{{ space.factors[activeTooltip.fidx] }}:</strong> 
          {{ activeTooltip.value.toFixed(2) }} probability
        </div>
      </div>
    </div>

    <!-- Color Legend -->
    <div v-if="heatmapData" class="color-legend">
      <div 
        v-for="(stop, index) in colorStops" 
        :key="index" 
        class="legend-stop"
        :style="{ backgroundColor: stop.color }"
      >
        {{ stop.label }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      selectedHouses: [],
      heatmapData: null,
      activeTooltip: null,
      tooltipStyle: {},
      colorStops: [
        { value: 0, color: '#2c7bb6', label: '0%' },
        { value: 0.5, color: '#ffff8c', label: '50%' },
        { value: 1, color: '#d7191c', label: '100%' }
      ],
      houses: [],
      newHouseName: '',
      apiBaseUrl: 'http://localhost:5000/api',
      space: { id: null, factors: [] },
      cellSize: 80
    }
  },
  computed: {
    comparisons() {
      return this.heatmapData?.comparisons || []
    }
  },
  async mounted() {
    await this.fetchSpaceDetails()
    await this.fetchHouses()
  },
  methods: {
    toggleHouseSelection(houseId) {
      const index = this.selectedHouses.indexOf(houseId)
      if (index === -1) {
        this.selectedHouses.push(houseId)
      } else {
        this.selectedHouses.splice(index, 1)
      }
    },
    async runDiscernabilityAnalysis() {
      try {
        const response = await axios.post(
          `${this.apiBaseUrl}/analysis/${this.space.id}`,
          {
            house_ids: this.selectedHouses,
            method: 'discernability_analysis'
          }
        )
        this.heatmapData = response.data
      } catch (error) {
        console.error('Analysis failed:', error)
        alert('Analysis failed: ' + (error.response?.data?.error || 'Server error'))
      }
    },
    getColor(value) {
      const ratio = Math.min(Math.max(value, 0), 1)
      return this.interpolateColor('#2c7bb6', '#d7191c', ratio)
    },
    interpolateColor(color1, color2, ratio) {
      const r1 = parseInt(color1.substring(1,3), 16)
      const g1 = parseInt(color1.substring(3,5), 16)
      const b1 = parseInt(color1.substring(5,7), 16)
      
      const r2 = parseInt(color2.substring(1,3), 16)
      const g2 = parseInt(color2.substring(3,5), 16)
      const b2 = parseInt(color2.substring(5,7), 16)
      
      const r = Math.round(r1 + (r2 - r1) * ratio)
      const g = Math.round(g1 + (g2 - g1) * ratio)
      const b = Math.round(b1 + (b2 - b1) * ratio)
      
      return `#${[r,g,b].map(x => x.toString(16).padStart(2,'0')).join('')}`
    },
    showTooltip(event, comparison, fidx, value) {
      this.activeTooltip = {
        comparison: `${this.getHouseName(comparison.house1)} vs ${this.getHouseName(comparison.house2)}`,
        fidx,
        value
      }
      
      const rect = event.target.getBoundingClientRect()
      this.tooltipStyle = {
        left: `${rect.left + window.scrollX}px`,
        top: `${rect.bottom + window.scrollY + 10}px`
      }
    },
    getHouseName(houseId) {
      return this.houses.find(h => h.id === houseId)?.name || ''
    },
    async uploadHouse() {
      const fileInput = this.$refs.houseFile
      if (!fileInput.files.length) {
        alert('Please select a CSV file.')
        return
      }

      const formData = new FormData()
      formData.append('file', fileInput.files[0])
      if (this.newHouseName.trim()) {
        formData.append('name', this.newHouseName.trim())
      }

      try {
        const response = await axios.post(
          `${this.apiBaseUrl}/spaces/${this.space.id}/houses`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )

        this.houses.push(response.data)
        this.newHouseName = ''
        fileInput.value = ''
        alert('House uploaded successfully!')
      } catch (error) {
        console.error('Upload failed:', error)
        alert('Upload failed: ' + (error.response?.data?.error || 'Server error'))
      }
    },
    async fetchHouses() {
      try {
        const response = await axios.get(`${this.apiBaseUrl}/spaces/${this.space.id}/houses`)
        this.houses = response.data.houses
      } catch (error) {
        console.error('Failed to fetch houses:', error)
      }
    },
    async fetchSpaceDetails() {
      try {
        const response = await axios.get(`${this.apiBaseUrl}/spaces/${this.$route.params.spaceId}`)
        this.space = response.data
      } catch (error) {
        console.error('Failed to fetch space details:', error)
      }
    }
  }
}
</script>

<style scoped>
.upload-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.upload-btn {
  margin-left: 1rem;
  background: #4caf50;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.upload-btn:hover {
  transform: translateY(-1px);
}

.houses-list ul {
  list-style: none;
  padding: 0;
}

.houses-list li {
  padding: 0.8rem;
  margin-bottom: 0.4rem;
  background: #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.houses-list li.selected {
  background: #2196F3;
  color: white;
  transform: translateX(5px);
}

.analysis-controls {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.analyze-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 1rem;
}

.analyze-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
}

.heatmap-container {
  position: relative;
  margin: 2rem 0;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.heatmap-wrapper {
  overflow-x: auto;
  padding-bottom: 1rem;
}

.factors-header {
  display: flex;
  gap: 4px;
  margin-left: 200px;
  padding-bottom: 8px;
}

.factor-header {
  flex-shrink: 0;
  text-align: center;
  font-weight: 600;
  font-size: 0.9em;
  color: #444;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.heatmap-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comparison-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.comparison-label {
  width: 200px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: 500;
  flex-shrink: 0;
}

.factors-row {
  display: flex;
  gap: 4px;
}

.factor-cell {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
  animation: cellEnter 0.3s ease forwards;
  opacity: 0;
  transform: scale(0.9);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.factor-cell:hover {
  transform: scale(1.05);
  z-index: 2;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.cell-value {
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  font-size: 0.85em;
  font-weight: 500;
}

@keyframes cellEnter {
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.heatmap-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px;
  border-radius: 6px;
  pointer-events: none;
  backdrop-filter: blur(2px);
  transform: translateX(-50%);
  min-width: 200px;
  z-index: 100;
}

.tooltip-header {
  font-weight: 600;
  margin-bottom: 6px;
  color: #fff;
}

.tooltip-body {
  font-size: 0.9em;
  color: #eee;
}

.color-legend {
  display: flex;
  margin-top: 1.5rem;
  gap: 2px;
  height: 24px;
  border-radius: 4px;
  overflow: hidden;
}

.legend-stop {
  flex: 1;
  text-align: center;
  padding: 4px 8px;
  font-size: 0.8em;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.heatmap-row-enter-active,
.heatmap-row-leave-active {
  transition: all 0.3s ease;
}

.heatmap-row-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.heatmap-row-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.heatmap-cell-enter-active {
  transition: all 0.3s ease;
}

.heatmap-cell-enter-from {
  opacity: 0;
  transform: scale(0.8);
}
</style>