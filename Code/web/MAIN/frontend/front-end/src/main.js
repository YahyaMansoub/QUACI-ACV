import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  // Make sure this path is correct

createApp(App)
  .use(router)  // This is the critical line
  .mount('#app')