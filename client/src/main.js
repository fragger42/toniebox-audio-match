import 'bootstrap/dist/css/bootstrap.css';
import * as Vue from 'vue';
import * as VueRouter from 'vue-router';
import AudioBooks from './components/AudioBooks.vue';
import App from './App.vue';

const routes = [
  {
    path: '/',
    name: 'AudioBooks',
    component: AudioBooks,
  },
];

const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(process.env.BASE_URL),
  routes,
});

const app = Vue.createApp(App);
app.config.globalProperties.$backendUrl = `${process.env.VUE_APP_BACKEND_SCHEME}://${process.env.VUE_APP_BACKEND_HOST}:${process.env.VUE_APP_BACKEND_PORT}`;
app.use(router).mount('#app');
