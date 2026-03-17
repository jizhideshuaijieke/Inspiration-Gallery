import Vue from 'vue'
import VueRouter from 'vue-router'
import LoginView from '../views/LoginView.vue'
import MainLayoutView from '../views/MainLayoutView.vue'
import HallView from '../views/HallView.vue'
import CreateView from '../views/CreateView.vue'
import NoticeView from '../views/NoticeView.vue'
import MeView from '../views/MeView.vue'
import AdminLayoutView from '../views/admin/AdminLayoutView.vue'
import AdminArtworksView from '../views/admin/AdminArtworksView.vue'
import AdminCommentsView from '../views/admin/AdminCommentsView.vue'
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import { isAdminToken } from '../utils/auth'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayoutView,
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/artworks' },
        { path: 'artworks', component: AdminArtworksView },
        { path: 'comments', component: AdminCommentsView },
        { path: 'users', component: AdminUsersView }
      ]
    },
    {
      path: '/',
      component: MainLayoutView,
      children: [
        { path: '', redirect: '/hall' },
        { path: 'hall', component: HallView },
        { path: 'create', component: CreateView, meta: { keepAlive: true } },
        { path: 'notice', component: NoticeView },
        { path: 'users/:userId', component: MeView },
        { path: 'me', component: MeView }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAdmin) && !isAdminToken()) {
    next('/login')
    return
  }

  next()
})

export default router
