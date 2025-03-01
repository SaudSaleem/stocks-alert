import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    // Redirect any unknown routes to login
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ],
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user') !== null;
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if trying to access a protected route without being authenticated
    next({ name: 'login' });
  } else {
    // Continue to the requested route
    next();
  }
});

export default router
