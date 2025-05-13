<script>
import axios from 'axios'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale
} from 'chart.js'
import { Bar, Line, Radar } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, LineElement, PointElement, CategoryScale, LinearScale, RadialLinearScale)

export default {
  components: {
    BarChart: {
      extends: Bar,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options)
      },
      watch: {
        chartData(newData) {
          this.renderChart(newData, this.options)
        }
      }
    },
    LineChart: {
      extends: Line,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options)
      },
      watch: {
        chartData(newData) {
          this.renderChart(newData, this.options)
        }
      }
    },
    RadarChart: {
      extends: Radar,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options)
      },
      watch: {
        chartData(newData) {
          this.renderChart(newData, this.options)
        }
      }
    }
  },

  data() {
    return {
      selectedHouses: [],
      heatmapData: null,
      activeTooltip: null,
      tooltipStyle: {},
      houses: [],
      newHouseName: '',
      space: { id: null, name: '', factors: [] },
      apiBaseUrl: 'http://localhost:5000/api',
      cellSize: 80,
      barColors: ['#1976d2', '#43a047', '#d32f2f', '#fbc02d', '#8e24aa', '#00897b', '#e64a19', '#7b1fa2', '#388e3c', '#c62828'],
      barChartData: null,
      barChartOptions: {
        responsive: true,
        plugins: {
          legend: { display: true },
          title: { display: true, text: `Simulations and Impact Score per House (${new Date().toLocaleDateString()})` }
        },
        scales: {
          x: { title: { display: true, text: 'Houses' } },
          y: { beginAtZero: true, title: { display: true, text: 'Value' } }
        }
      },
      lineChartData: null,
      lineChartOptions: {
        responsive: true,
        plugins: {
          legend: { display: true },
          title: { display: true, text: `Simulation Evolution (${new Date().toLocaleDateString()})` }
        },
        scales: {
          x: { title: { display: true, text: 'Houses' } },
          y: { beginAtZero: true, title: { display: true, text: 'Simulations' } }
        }
      },
      radarChartData: null,
      radarChartOptions: {
        responsive: true,
        plugins: {
          legend: { display: true },
          title: { display: true, text: 'House Comparison by Factors' }
        }
      },
      colorStops: [
        { value: 0, color: '#2c7bb6', label: '0%' },
        { value: 0.5, color: '#ffff8c', label: '50%' },
        { value: 1, color: '#d7191c', label: '100%' }
      ]
    }
  },

  computed: {
    comparisons() {
      return this.heatmapData?.comparisons || []
    }
  },

  created() {
    this.space.id = this.$route?.params?.spaceId || null
    if (!this.space.id) console.error('Missing spaceId in route')
  },

  async mounted() {
    await this.fetchSpaceDetails()
    await this.fetchHouses()
  },

  methods: {
    toggleHouseSelection(houseId) {
      const i = this.selectedHouses.indexOf(houseId)
      i === -1 ? this.selectedHouses.push(houseId) : this.selectedHouses.splice(i, 1)
    },

    async runDiscernabilityAnalysis() {
      try {
        const response = await axios.post(`${this.apiBaseUrl}/analysis/${this.space.id}`, {
          house_ids: this.selectedHouses,
          method: 'discernability_analysis'
        })
        this.heatmapData = response.data
        this.updateRadarChart()
      } catch (error) {
        console.error('Analysis failed:', error)
        alert('Analysis failed: ' + (error.response?.data?.error || 'Server error'))
      }
    },

    getColor(value) {
      const interpolate = this.interpolateColor
      const [start, middle, end] = ['#1976d2', '#43a047', '#d32f2f']
      return value <= 0.5
        ? interpolate(start, middle, value / 0.5)
        : interpolate(middle, end, (value - 0.5) / 0.5)
    },

    interpolateColor(color1, color2, ratio) {
      const hex = (c) => parseInt(c, 16)
      const r = Math.round(hex(color1.slice(1, 3)) + ratio * (hex(color2.slice(1, 3)) - hex(color1.slice(1, 3))))
      const g = Math.round(hex(color1.slice(3, 5)) + ratio * (hex(color2.slice(3, 5)) - hex(color1.slice(3, 5))))
      const b = Math.round(hex(color1.slice(5, 7)) + ratio * (hex(color2.slice(5, 7)) - hex(color1.slice(5, 7))))
      return `#${[r, g, b].map(x => x.toString(16).padStart(2, '0')).join('')}`
    },

    showTooltip(event, comparison, fidx, value) {
      const rect = event.target.getBoundingClientRect()
      this.activeTooltip = {
        comparison: `${this.getHouseName(comparison.house1)} vs ${this.getHouseName(comparison.house2)}`,
        fidx,
        value
      }
      this.tooltipStyle = {
        left: `${rect.left + window.scrollX}px`,
        top: `${rect.bottom + window.scrollY + 10}px`
      }
    },

    getHouseName(id) {
      return this.houses.find(h => h.id === id)?.name || ''
    },

    async uploadHouse() {
      const file = this.$refs.houseFile?.files?.[0]
      if (!file) return alert('Please select a CSV file.')

      const formData = new FormData()
      formData.append('file', file)
      if (this.newHouseName.trim()) {
        formData.append('name', this.newHouseName.trim())
      }

      try {
        await axios.post(`${this.apiBaseUrl}/spaces/${this.space.id}/houses`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.newHouseName = ''
        this.$refs.houseFile.value = null
        await this.fetchHouses()
        alert('House uploaded successfully!')
      } catch (e) {
        console.error('Upload failed:', e)
        alert('Upload failed: ' + (e.response?.data?.error || 'Server error'))
      }
    },

    async fetchHouses() {
      try {
        const { data } = await axios.get(`${this.apiBaseUrl}/spaces/${this.space.id}/houses`)
        this.houses = data.houses || []
        this.updateBarChart()
      } catch (e) {
        console.error('Failed to fetch houses:', e)
      }
    },

    async fetchSpaceDetails() {
      try {
        const { data } = await axios.get(`${this.apiBaseUrl}/spaces/${this.space.id}`)
        this.space = data
      } catch (e) {
        console.error('Failed to fetch space details:', e)
        this.space = { id: this.space.id, name: 'Unknown', factors: [] }
      }
    },

    updateBarChart() {
      const names = this.houses.map(h => h.name)
      this.barChartData = {
        labels: names,
        datasets: [
          {
            label: 'Simulations',
            backgroundColor: names.map((_, i) => this.barColors[i % this.barColors.length]),
            data: this.houses.map(h => h.simulations)
          },
          {
            label: 'Impact Score',
            backgroundColor: names.map((_, i) => this.barColors[(i + 3) % this.barColors.length] + '99'),
            data: this.houses.map(() => Math.round(Math.random() * 100))
          }
        ]
      }
      this.updateLineChart()
      this.updateRadarChart()
    },

    updateLineChart() {
      const names = this.houses.map(h => h.name)
      this.lineChartData = {
        labels: names,
        datasets: [
          {
            label: 'Simulations',
            borderColor: this.barColors[0],
            backgroundColor: this.barColors[0] + '33',
            data: this.houses.map(h => h.simulations),
            fill: true
          },
          {
            label: 'Impact Score',
            borderColor: this.barColors[3],
            backgroundColor: this.barColors[3] + '33',
            data: this.houses.map(() => Math.round(Math.random() * 100)),
            fill: true
          }
        ]
      }
    },

    updateRadarChart() {
      if (!this.heatmapData?.comparisons?.length) return (this.radarChartData = null)
      const [comp] = this.heatmapData.comparisons
      this.radarChartData = {
        labels: this.space.factors,
        datasets: [
          {
            label: this.getHouseName(comp.house1),
            data: comp.values,
            backgroundColor: 'rgba(76,175,80,0.2)',
            borderColor: '#4CAF50',
            pointBackgroundColor: '#4CAF50'
          },
          {
            label: this.getHouseName(comp.house2),
            data: comp.values.map(v => 1 - v),
            backgroundColor: 'rgba(25,118,210,0.2)',
            borderColor: '#1976d2',
            pointBackgroundColor: '#1976d2'
          }
        ]
      }
    }
  }
}
</script>
