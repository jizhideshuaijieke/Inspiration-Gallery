<template>
  <div class="admin-shell">
    <HallSidebar :tabs="tabs" :active-tab="activeTab" @change="onTabChange" @logout="onLogout" />
    <main class="main-panel">
      <router-view />
    </main>
  </div>
</template>

<script>
import HallSidebar from '../../components/hall/HallSidebar.vue'

export default {
  name: 'AdminLayoutView',
  components: {
    HallSidebar
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
      const segment = (this.$route.path.split('/')[2] || 'artworks').toLowerCase()
      return this.tabs.some((tab) => tab.key === segment) ? segment : 'artworks'
    }
  },
  methods: {
    onTabChange(tabKey) {
      const targetPath = `/admin/${tabKey}`
      if (this.$route.path !== targetPath) this.$router.push(targetPath)
    },
    onLogout() {
      localStorage.removeItem('token')
      this.$router.replace('/login')
    }
  }
}
</script>

<style scoped lang="scss">
.admin-shell {
  @include app-shell;
}

.main-panel {
  @include app-main-panel;
}

@media (max-width: 900px) {
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
