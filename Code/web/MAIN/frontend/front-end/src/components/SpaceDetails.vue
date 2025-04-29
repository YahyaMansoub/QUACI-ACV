<template>
  <div class="space-details">
    <!-- Existing header and upload section -->
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
    <li v-for="house in houses" :key="house.id" @click="toggleHouseSelection(house.id)" :class="{ selected: selectedHouses.includes(house.id) }">
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

    <!-- Heatmap Display -->
    <div v-if="heatmapData" class="heatmap-container">
      <div class="heatmap">
        <!-- Column Labels -->
        <div class="heatmap-axis heatmap-columns">
          <div 
            v-for="(house, colIndex) in houseList" 
            :key="colIndex" 
            class="heatmap-label"
          >
            {{ house.name }}
          </div>
        </div>
        
        <!-- Row Labels and Cells -->
        <div 
          v-for="(rowHouse, rowIndex) in houseList" 
          :key="rowIndex" 
          class="heatmap-row"
        >
          <div class="heatmap-axis heatmap-rows">
            {{ rowHouse.name }}
          </div>
          <div 
            v-for="(colHouse, colIndex) in houseList" 
            :key="colIndex" 
            class="heatmap-cell"
            :style="cellStyle(rowIndex, colIndex)"
            @mouseenter="setTooltip(rowIndex, colIndex)"
          >
            {{ cellValue(rowIndex, colIndex) }}
          </div>
        </div>
      </div>

      <!-- Tooltip -->
      <div 
        v-if="activeTooltip" 
        class="heatmap-tooltip"
        :style="tooltipPosition"
      >
        {{ activeTooltip }}
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
      // Existing data...
      selectedHouses: [],
      heatmapData: null,
      activeTooltip: null,
      tooltipPosition: { left: '0px', top: '0px' },
      colorStops: [
        { value: 0, color: '#2c7bb6', label: '0%' },
        { value: 0.5, color: '#ffff8c', label: '50%' },
        { value: 1, color: '#d7191c', label: '100%' }
      ],
      houses: [], // list of all houses
newHouseName: '', // optional custom house name
apiBaseUrl: 'http://localhost:5000/api', // adjust if needed
space: { id: 1 }, // TEMP fake, you must replace with your actual space info

    }
  },
  computed: {
    houseList() {
      return this.houses.filter(h => this.selectedHouses.includes(h.id))
    }
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
        this.heatmapData = response.data.heatmap_data
      } catch (error) {
        console.error('Analysis failed:', error)
        alert('Analysis failed: ' + (error.response?.data?.error || 'Server error'))
      }
    },
    cellValue(rowIndex, colIndex) {
      const rowId = this.houseList[rowIndex].id
      const colId = this.houseList[colIndex].id
      return this.heatmapData[rowId][colId]?.toFixed(2) || '-'
    },
    cellStyle(rowIndex, colIndex) {
      const value = parseFloat(this.cellValue(rowIndex, colIndex))
      if (isNaN(value)) return { backgroundColor: '#f0f0f0' }
      
      const color = this.getColor(value)
      return { 
        backgroundColor: color,
        color: value > 0.6 ? 'white' : 'black'
      }
    },
    getColor(value) {
      const stops = this.colorStops
      if (value <= stops[0].value) return stops[0].color
      if (value >= stops[stops.length-1].value) return stops[stops.length-1].color
      
      for (let i = 1; i < stops.length; i++) {
        if (value <= stops[i].value) {
          const ratio = (value - stops[i-1].value) / (stops[i].value - stops[i-1].value)
          return this.interpolateColor(stops[i-1].color, stops[i].color, ratio)
        }
      }
      return stops[0].color
    },
    interpolateColor(color1, color2, ratio) {
      const r1 = parseInt(color1.substring(1,3)), g1 = parseInt(color1.substring(3,5)), b1 = parseInt(color1.substring(5,7))
      const r2 = parseInt(color2.substring(1,3)), g2 = parseInt(color2.substring(3,5)), b2 = parseInt(color2.substring(5,7))
      
      const r = Math.round(r1 + (r2 - r1) * ratio)
      const g = Math.round(g1 + (g2 - g1) * ratio)
      const b = Math.round(b1 + (b2 - b1) * ratio)
      
      return `#${[r,g,b].map(x => x.toString(16).padStart(2,'0')).join('')}`
    },
    setTooltip(rowIndex, colIndex) {
      const rowHouse = this.houseList[rowIndex]
      const colHouse = this.houseList[colIndex]
      this.activeTooltip = `${rowHouse.name} vs ${colHouse.name}: ${this.cellValue(rowIndex, colIndex)}`
      
      const cell = event.target.getBoundingClientRect()
      this.tooltipPosition = {
        left: `${cell.left + window.scrollX + cell.width/2}px`,
        top: `${cell.top + window.scrollY - 30}px`
      }
    },
    async uploadHouse() {
  const fileInput = this.$refs.houseFile;
  if (!fileInput.files.length) {
    alert('Please select a CSV file.');
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  if (this.newHouseName.trim()) {
    formData.append('name', this.newHouseName.trim());
  }

  try {
    const response = await axios.post(
      `${this.apiBaseUrl}/spaces/${this.space.id}/houses`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );

    this.houses.push(response.data); // add newly uploaded house
    this.newHouseName = '';
    fileInput.value = ''; // reset file input
    alert('House uploaded successfully!');
  } catch (error) {
    console.error('Upload failed:', error);
    alert('Upload failed: ' + (error.response?.data?.error || 'Server error'));
  }
},async mounted() {
  await this.fetchHouses();
},

  async fetchHouses() {
    try {
      const response = await axios.get(`${this.apiBaseUrl}/spaces/${this.space.id}/houses`);
      this.houses = response.data.houses; // assumes backend gives {houses: [...]}
    } catch (error) {
      console.error('Failed to fetch houses:', error);
    }
  }
}


  }

</script>

<style scoped>
.heatmap-container {
  position: relative;
  margin: 2rem 0;
  overflow-x: auto;
}

.heatmap {
  display: grid;
  grid-template-columns: auto repeat(auto-fit, minmax(60px, 1fr));
  gap: 1px;
  background: #ddd;
  min-width: 600px;
}

.heatmap-row {
  display: contents;
}

.heatmap-cell {
  padding: 1rem;
  text-align: center;
  background: white;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  cursor: pointer;
}

.heatmap-cell:hover {
  transform: scale(1.1);
  z-index: 2;
  box-shadow: 0 0 8px rgba(0,0,0,0.2);
}

.heatmap-axis {
  padding: 1rem;
  background: #f8f9fa;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-columns {
  position: sticky;
  top: 0;
  z-index: 1;
}

.color-legend {
  display: flex;
  gap: 2px;
  margin-top: 1rem;
  height: 30px;
}

.legend-stop {
  flex: 1;
  text-align: center;
  padding: 0.3rem;
  font-size: 0.8em;
  color: black;
}

.heatmap-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  pointer-events: none;
  transform: translate(-50%, -100%);
  white-space: nowrap;
}

.analysis-controls {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.analyze-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 1rem;
}

.analyze-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
}
.upload-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.upload-btn {
  margin-left: 1rem;
  background: #4caf50;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
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
  transition: background 0.2s;
}

.houses-list li.selected {
  background: #2196F3;
  color: white;
}

</style>