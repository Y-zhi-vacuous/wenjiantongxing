// API base URL — change this when deploying to a new backend
const isCapacitor = typeof (window as any).Capacitor !== 'undefined'

export const API_BASE_URL = isCapacitor
  ? 'https://wenjiantongxing.fly.dev/api'  // TODO: update to your deployed backend URL
  : '/api'
