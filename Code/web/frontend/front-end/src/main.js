import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { createPinia } from 'pinia'
import VueECharts from 'vue-echarts'
import { use } from 'echarts/core'
// Import only necessary ECharts modules
import {
  CanvasRenderer
} from 'echarts/renderers';
import {
  BarChart,
  LineChart,
  PieChart,
  HeatmapChart
} from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
  DatasetComponent
} from 'echarts/components';

// Register ECharts modules globally
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
  DatasetComponent
]);

const app = createApp(App)
const pinia = createPinia()             // ✅ this line is new
app.use(pinia)                          // ✅ register pinia before using stores
app.use(router)
app.component('vue-echarts', VueECharts)
app.mount('#app')