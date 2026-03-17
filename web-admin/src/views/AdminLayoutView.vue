<template>
  <div class="admin-shell">
    <AdminSidebar :tabs="tabs" :active-tab="activeTab" @change="onTabChange" @logout="onLogout" />
    <main class="main-panel">
      <router-view />
    </main>
  </div>
</template>

<script>
import AdminSidebar from '../components/AdminSidebar.vue'
import { clearAdminSession } from '../utils/auth'

export default {
  name: 'AdminLayoutView',
  components: {
    AdminSidebar
  },
  data() {
    return {
      tabs: [
        { key: 'artworks', label: '作品' },
        { key: 'comments', label: '评论' },
        { key: 'users', label: '用户' }
      ]
    }
  },
  computed: {
    activeTab() {
      const segment = (this.$route.path.split('/')[1] || 'artworks').toLowerCase()
      return this.tabs.some((tab) => tab.key === segment) ? segment : 'artworks'
    }
  },
  methods: {
    onTabChange(tabKey) {
      const targetPath = `/${tabKey}`
      if (this.$route.path !== targetPath) this.$router.push(targetPath)
    },
    onLogout() {
      clearAdminSession()
      this.$router.replace('/login')
    }
  }
}
</script>

<style scoped>
.admin-shell {
  height: 100vh;
  min-height: 100vh;
  background: radial-gradient(circle at 15% 20%, #f0f2ed 0%, #f8f8f6 40%, #f4f4f0 100%);
  color: var(--ink);
  display: flex;
  overflow: hidden;
}

.main-panel {
  flex: 1;
  min-width: 0;
  height: 100vh;
  padding: 20px 24px 30px;
  display: flex;
  overflow: hidden;
}

.main-panel > * {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 980px) {
  .admin-shell {
    display: block;
    height: auto;
    overflow: visible;
  }

  .main-panel {
    height: auto;
    padding: 14px;
    display: block;
    overflow: visible;
  }

  .main-panel > * {
    overflow: visible;
  }
}
</style>
