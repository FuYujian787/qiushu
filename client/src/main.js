import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

// 引入苹果液态玻璃风格样式
import './assets/apple-liquid-glass.css'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
