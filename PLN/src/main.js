import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { io } from "socket.io-client"

import App from './App.vue'
import router from './router'
import axios from 'axios'
import Toast from "vue-toastification"

// Import CSS
import 'bootstrap'
import "vue-toastification/dist/index.css"
import '@/assets/vendors/css/vendor.bundle.base.css'
import '@/assets/vendors/mdi/css/materialdesignicons.min.css'
import '@/assets/vendors/jvectormap/jquery-jvectormap.css'
import '@/assets/vendors/flag-icon-css/css/flag-icon.min.css'
import '@/assets/css/main.css'
import '@/assets/css/home.css'
import '@/assets/css/style.css'

// Import JS
import '@/assets/vendors/chart.js/Chart.min.js'
import '@/assets/vendors/jvectormap/jquery-jvectormap.min.js'
import '@/assets/vendors/jvectormap/jquery-jvectormap-world-mill-en.js'
import '@/assets/js/hoverable-collapse.js'
import '@/assets/js/misc.js'
import '@/assets/js/off-canvas.js'

// Create app
const app = createApp(App)

const socket = 'http://localhost:8082'
app.provide('socket', io(socket))

const serverBaseUrl = 'http://isaws-project.test'
app.provide('serverBaseUrl', serverBaseUrl)

const elasticsearch = 'http://82.155.130.155:9200/'
app.provide('elasticsearch', elasticsearch)

// Default Axios configuration
axios.defaults.baseURL = serverBaseUrl + '/api'
axios.defaults.headers.common['Content-type'] = 'application/json'
app.provide('axios', axios) // Provide axios instance

// Create redditAxios instance
const redditAxios = axios.create({
    baseURL: 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json'
    }
})
app.provide('redditAxios', redditAxios)

// Create elasticAxios instance
const elasticAxios = axios.create({
    baseURL: 'http://82.155.130.155:9200/',
    headers: {
        'Content-Type': 'application/json'
    }
})
app.provide('elasticAxios', elasticAxios)

// Create toast notification
app.use(Toast, {
    position: "top-right",
    timeout: 3000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: true,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false,
    toastClassName: "custom-toast"
})

// App setup
app.use(createPinia())
app.use(router)
app.mount('#app')
