import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/extract',
      name: 'extract',
      component: () => import('../views/ExtractView.vue')
    },
    {
      path: '/verify',
      name: 'verify',
      component: () => import('../views/VerifyView.vue')
    },
    {
      path: '/generate-vc',
      name: 'generate-vc',
      component: () => import('../views/GenerateVCView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    }
  ]
})

export default router

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register', '/'];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('token');

  if (authRequired && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});
