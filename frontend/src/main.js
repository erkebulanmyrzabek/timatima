import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import axios from 'axios';
import './assets/css/main.css';

// Установка глобальных заголовков для axios
const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

const app = createApp(App);

app.use(router)
   .use(store)
   .mount('#app'); 