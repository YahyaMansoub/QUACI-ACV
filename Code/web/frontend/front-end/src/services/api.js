import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:5000/api' })

export const getHouses = (spaceId) => api.get(`/spaces/${spaceId}/houses`)
export const getEnvironmentalImpact = (id) => api.get(`/houses/${id}/environmental-impact`)
export const getMaterials = (id) => api.get(`/houses/${id}/materials`)
export const getUncertaintyAnalysis = (id) => api.get(`/houses/${id}/uncertainty-analysis`)
export const getSMD = () => api.get('/comparison/smd')
export const getDRD = () => api.get('/comparison/drd')
export const getDiscernability = () => api.get('/comparison/discernability')
export const getHeijungs = () => api.get('/comparison/heijungs')
export const getRankingProbabilities = () => api.get('/comparison/ranking-probabilities')

// NEW: Upload & Analysis-related
export const uploadCSV = (formData) =>
  api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

export const getUploadedResult = (method) =>
  api.get(`/upload/results/${method}`)
