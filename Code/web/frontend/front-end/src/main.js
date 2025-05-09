import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import VueECharts from 'vue-echarts';
import { use, init } from 'echarts/core';

// Optionally import and register only required ECharts modules
import {
  CanvasRenderer,
} from 'echarts/renderers';
import {
  BarChart,
  LineChart,
  PieChart,
  HeatmapChart,
} from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
  DatasetComponent,
} from 'echarts/components';

// Register the ECharts modules
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
  DatasetComponent,
]);

// Create the Vue app
const app = createApp(App);

// Register vue-echarts as a global component and provide the ECharts instance
app.component('vue-echarts', VueECharts, {
  init: (el) => init(el, null, { renderer: 'canvas' }),
});

// Use the router
app.use(router);

// Mount the app
app.mount('#app');