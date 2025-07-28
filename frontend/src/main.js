import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
// import './assets/css/theme.css';

import Vue3Toastify from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

const app = createApp(App);

app.use(router);
app.use(Vue3Toastify, {
    "type": "default",
    "position": "top-center",
    "transition": "slide",
    "closeOnClick": true,
    "pauseOnFocusLoss": true,
    "pauseOnHover": false,
    "draggable": true,
    "draggablePercent": 0.6,
    "closeButton": true
});

app.mount('#app');