import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Plugin Vuetify
import {vuetify} from './plugins/vuetify'

const app = createApp(App)

app.config.devtools = false

app.use(createPinia())
app.use(router)

// Plugin Vuetify
app.use(vuetify)

app.mount('#app')

