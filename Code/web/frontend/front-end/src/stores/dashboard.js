import { defineStore } from 'pinia'
import {
  getHouses,
  getEnvironmentalImpact,
  getMaterials,
  getUncertaintyAnalysis,
  getSMD,
  getDRD,
  getDiscernability,
  getHeijungs,
  getRankingProbabilities
} from '../services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    houses: [],
    selectedHouseId: null,
    envImpact: null,
    materials: [],
    uncertainty: null,
    smd: null,
    drd: null,
    discern: null,
    heijungs: null,
    ranking: null,
    loading: {
      houses: false,
      data: false
    },
    error: null
  }),

  actions: {
    async fetchHouses() {
      this.loading.houses = true
      this.error = null
      try {
        const res = await getHouses()
        this.houses = res.data || []
      } catch (e) {
        console.error('Error fetching houses:', e)
        this.error = e.message || 'Failed to load houses.'
      } finally {
        this.loading.houses = false
      }
    },

    async selectHouse(id) {
      this.selectedHouseId = id
      this.loading.data = true
      this.error = null
      try {
        const [
          impactRes,
          matRes,
          uncerRes,
          smdRes,
          drdRes,
          discRes,
          heijRes,
          rankRes
        ] = await Promise.all([
          getEnvironmentalImpact(id),
          getMaterials(id),
          getUncertaintyAnalysis(id),
          getSMD(),
          getDRD(),
          getDiscernability(),
          getHeijungs(),
          getRankingProbabilities()
        ])

        this.envImpact = impactRes.data || null
        this.materials = matRes.data || []
        this.uncertainty = uncerRes.data || null
        this.smd = smdRes.data || null
        this.drd = drdRes.data || null
        this.discern = discRes.data || null
        this.heijungs = heijRes.data || null
        this.ranking = rankRes.data || null

      } catch (e) {
        console.error('Error loading house data:', e)
        this.error = e.message || 'Failed to load house data.'
      } finally {
        this.loading.data = false
      }
    }
  }
})
