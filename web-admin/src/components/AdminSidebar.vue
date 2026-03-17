<template>
  <aside class="side-nav">
    <div class="brand">
      <span class="brand-dot"></span>
      <span>灵感画廊</span>
    </div>
    <p class="brand-subtitle">管理端</p>

    <nav class="tab-nav">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="$emit('change', tab.key)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="menu-wrap">
      <button
        type="button"
        class="menu-toggle"
        aria-label="更多操作"
        @click.stop="toggleMenu"
      >
        <span class="menu-icon" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      <div v-if="menuOpen" class="menu-pop" @click.stop>
        <button type="button" class="menu-item danger" @click="onLogout">
          退出登录
        </button>
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AdminSidebar',
  props: {
    tabs: {
      type: Array,
      default: () => []
    },
    activeTab: {
      type: String,
      default: 'artworks'
    }
  },
  data() {
    return {
      menuOpen: false
    }
  },
  watch: {
    activeTab() {
      this.menuOpen = false
    }
  },
  mounted() {
    window.addEventListener('click', this.closeMenu)
  },
  beforeDestroy() {
    window.removeEventListener('click', this.closeMenu)
  },
  methods: {
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    closeMenu() {
      this.menuOpen = false
    },
    onLogout() {
      this.menuOpen = false
      this.$emit('logout')
    }
  }
}
</script>

<style scoped>
.side-nav {
  width: 236px;
  height: 100vh;
  padding: 24px 16px 18px;
  border-right: 1px solid var(--edge);
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: rgba(248, 248, 244, 0.9);
  backdrop-filter: blur(4px);
}

.brand {
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-subtitle {
  margin: 6px 0 18px 20px;
  color: var(--muted);
  font-size: 12px;
}

.brand-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 6px rgba(255, 51, 95, 0.14);
}

.tab-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tab-item {
  border: 0;
  border-radius: 14px;
  height: 46px;
  background: transparent;
  text-align: left;
  padding: 0 14px;
  font-size: 17px;
  color: var(--ink);
  cursor: pointer;
  transition: background 0.2s ease;
}

.tab-item:hover {
  background: #ecefe8;
}

.tab-item.active {
  background: #e2e8de;
  font-weight: 700;
}

.menu-wrap {
  margin-top: auto;
  position: relative;
  display: flex;
  justify-content: flex-start;
  padding: 18px 8px 4px;
}

.menu-toggle {
  min-width: 64px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.menu-toggle:hover {
  background: #ecefe8;
}

.menu-icon {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
}

.menu-icon span {
  display: block;
  width: 24px;
  height: 2.5px;
  border-radius: 999px;
  background: #454c46;
}

.menu-pop {
  position: absolute;
  bottom: 54px;
  left: 8px;
  min-width: 132px;
  padding: 8px;
  border: 1px solid #d9ded6;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 18px 44px rgba(24, 34, 27, 0.12);
}

.menu-item {
  width: 100%;
  border: 0;
  border-radius: 12px;
  background: transparent;
  text-align: left;
  padding: 10px 12px;
  font-size: 14px;
  color: #243027;
  cursor: pointer;
}

.menu-item:hover {
  background: #f4f6f2;
}

.menu-item.danger {
  color: #b13c57;
}

@media (max-width: 980px) {
  .side-nav {
    width: 100%;
    height: auto;
    position: static;
    border-right: 0;
    border-bottom: 1px solid var(--edge);
    padding: 16px;
  }

  .tab-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .tab-item {
    height: 40px;
    padding: 0 12px;
    font-size: 14px;
  }

  .menu-wrap {
    justify-content: flex-end;
    padding-top: 10px;
  }
}
</style>
