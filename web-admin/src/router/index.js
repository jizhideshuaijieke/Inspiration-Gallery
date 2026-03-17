import Vue from 'vue'
import VueRouter from 'vue-router'

import AdminLoginView from '../views/AdminLoginView.vue'
import AdminLayoutView from '../views/AdminLayoutView.vue'
import AdminArtworksView from '../views/AdminArtworksView.vue'
import AdminCommentsView from '../views/AdminCommentsView.vue'
import AdminUsersView from '../views/AdminUsersView.vue'
import { hasAdminSession } from '../utils/auth'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/login', component: AdminLoginView },
    {
      path: '/',
      component: AdminLayoutView,
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: '/artworks' },
        { path: 'artworks', component: AdminArtworksView },
        { path: 'comments', component: AdminCommentsView },
        { path: 'users', component: AdminUsersView }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAdmin) && !hasAdminSession()) {
    next('/login')
    return
  }

  if (to.path === '/login' && hasAdminSession()) {
    next('/artworks')
    return
  }

  next()
})

export default router
