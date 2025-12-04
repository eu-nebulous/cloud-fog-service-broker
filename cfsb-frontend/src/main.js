import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './index.js';

const pinia = createPinia();

const app = createApp(App);
app.use(router);
app.mount('#app');
app.use(pinia);
