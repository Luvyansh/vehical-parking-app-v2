import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
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
  },
  {
    path: '/user_dashboard',
    name: 'user_dashboard',
    component: () => import('../views/UserView.vue')
  },
  {
    path: '/admin_dashboard',
    name: 'admin_dashboard',
    component: () => import('../views/AdminView.vue')
  },
  {
    path: '/user_management',
    name: 'user_management',
    component: () => import('../views/UserManagerView.vue')
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/SearchView.vue')
  },
  {
    path: '/admin_summary',
    name: 'admin_summary',
    component: () => import('../views/AdminSummary.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
