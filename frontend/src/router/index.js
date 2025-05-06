import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';

// Компоненты страниц
import HomePage from '@/pages/HomePage.vue';
import NewsPage from '@/pages/NewsPage.vue';
import NewsDetailPage from '@/pages/NewsDetailPage.vue';
import LawyersPage from '@/pages/LawyersPage.vue';
import LawyerDetailPage from '@/pages/LawyerDetailPage.vue';
import MailPage from '@/pages/MailPage.vue';
import LoginPage from '@/pages/LoginPage.vue';
import RegisterPage from '@/pages/RegisterPage.vue';
import ProfilePage from '@/pages/ProfilePage.vue';
import NotFoundPage from '@/pages/NotFoundPage.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/news',
    name: 'news',
    component: NewsPage
  },
  {
    path: '/news/:id',
    name: 'news-detail',
    component: NewsDetailPage,
    props: true
  },
  {
    path: '/lawyers',
    name: 'lawyers',
    component: LawyersPage
  },
  {
    path: '/lawyers/:id',
    name: 'lawyer-detail',
    component: LawyerDetailPage,
    props: true
  },
  {
    path: '/mail',
    name: 'mail',
    component: MailPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { guestOnly: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    // Всегда прокручивать в верхнюю часть страницы
    return { top: 0 }
  }
});

// Навигационный хук для проверки аутентификации
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  // Проверка, требует ли маршрут аутентификации
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  }
  // Проверка, доступен ли маршрут только для гостей
  else if (to.matched.some(record => record.meta.guestOnly) && isAuthenticated) {
    next({ name: 'home' });
  }
  else {
    next();
  }
});

export default router; 