<template>
  <div class="xhs-shell">
    <HallSidebar :tabs="tabs" :active-tab="activeTab" @change="onTabChange" @logout="onLogout" />
    <main class="main-panel">
      <keep-alive include="CreateView">
        <router-view v-if="$route.meta.keepAlive" />
      </keep-alive>
      <router-view v-if="!$route.meta.keepAlive" />
    </main>
  </div>
</template>

<script>
import HallSidebar from '../components/hall/HallSidebar.vue'

export default {
  name: 'MainLayoutView',
  components: {
    HallSidebar
  },
  data() {
    return {
      tabs: [
        { key: 'hall', label: '大厅' },
        { key: 'create', label: '创作' },
        { key: 'notice', label: '通知' },
        { key: 'me', label: '我' }
      ]
    }
  },
  computed: {
    activeTab() {
      const segment = (this.$route.path.split('/')[1] || 'hall').toLowerCase()
      return this.tabs.some((tab) => tab.key === segment) ? segment : 'hall'
    }
  },
  methods: {
    onTabChange(tabKey) {
      const targetPath = `/${tabKey}`
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
.xhs-shell {
  @include app-shell;
}

.main-panel {
  @include app-main-panel;
}

@media (max-width: 900px) {
  .xhs-shell {
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
