<template>
  <section class="page">
    <AdminPanel title="用户列表" subtitle="只展示文档范围内的用户统计与状态信息">
      <AdminSearchBar v-model="filters.keyword" placeholder="搜索用户名">
        <button type="button" class="ghost-btn" @click="reloadList">搜索</button>
      </AdminSearchBar>

      <div class="filter-row">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          type="button"
          class="filter-pill"
          :class="{ active: filters.status === option.value }"
          @click="changeStatus(option.value)"
        >
          {{ option.label }}
        </button>
      </div>

      <div class="meta-row">
        <span>共 {{ total }} 位用户</span>
        <span v-if="loading">加载中...</span>
        <span v-else-if="errorMsg" class="error-text">{{ errorMsg }}</span>
      </div>

      <div class="list-scroll">
        <article
          v-for="item in users"
          :key="item.id"
          class="list-row"
          @click="openDetail(item)"
        >
          <div class="row-main">
            <div class="avatar">
              <img v-if="item.avatar_url" :src="item.avatar_url" alt="avatar" />
              <span v-else>{{ getInitial(item.username) }}</span>
            </div>

            <div class="row-copy">
              <div class="row-top">
                <strong class="row-title">{{ item.username }}</strong>
                <span class="status-tag" :class="`is-${item.status}`">{{ item.status }}</span>
              </div>
              <p class="row-subline">#{{ item.id }} · {{ item.role }}</p>
            </div>
          </div>

          <div class="row-stats">
            <span>作品 {{ item.artworks_count || 0 }}</span>
            <span>粉丝 {{ item.followers_count || 0 }}</span>
            <span>关注 {{ item.following_count || 0 }}</span>
          </div>
        </article>

        <div v-if="!loading && users.length === 0" class="empty-state">暂无用户数据</div>
      </div>

      <div class="footer-row">
        <button
          type="button"
          class="ghost-btn"
          :disabled="loading || !hasMore"
          @click="loadMore"
        >
          {{ hasMore ? '加载更多' : '没有更多了' }}
        </button>
      </div>
    </AdminPanel>

    <AdminModal :visible="detailVisible" @close="closeDetail">
      <section v-if="detailUser" class="detail-card">
        <div class="detail-head">
          <div class="detail-avatar">
            <img v-if="detailUser.avatar_url" :src="detailUser.avatar_url" alt="avatar" />
            <span v-else>{{ getInitial(detailUser.username) }}</span>
          </div>
          <div>
            <p class="detail-kicker">用户 #{{ detailUser.id }}</p>
            <h3 class="detail-title">{{ detailUser.username }}</h3>
            <p class="detail-subtitle">{{ detailUser.role }} · {{ detailUser.status }}</p>
          </div>
        </div>

        <div class="detail-grid">
          <article class="info-card">
            <span class="info-label">作品数</span>
            <strong>{{ detailUser.artworks_count || 0 }}</strong>
          </article>
          <article class="info-card">
            <span class="info-label">粉丝数</span>
            <strong>{{ detailUser.followers_count || 0 }}</strong>
          </article>
          <article class="info-card">
            <span class="info-label">关注数</span>
            <strong>{{ detailUser.following_count || 0 }}</strong>
          </article>
          <article class="info-card">
            <span class="info-label">更新时间</span>
            <strong>{{ formatDateTime(detailUser.updated_at) }}</strong>
          </article>
        </div>

        <p class="detail-time">创建时间：{{ formatDateTime(detailUser.created_at) }}</p>
      </section>
    </AdminModal>
  </section>
</template>

<script>
import AdminPanel from '../components/AdminPanel.vue'
import AdminSearchBar from '../components/AdminSearchBar.vue'
import AdminModal from '../components/AdminModal.vue'
import { getAdminUsers } from '../api/admin'

function resolveErrorMessage(error, fallback) {
  return (
    (error && error.response && error.response.data && error.response.data.message) ||
    fallback
  )
}

export default {
  name: 'AdminUsersView',
  components: {
    AdminPanel,
    AdminSearchBar,
    AdminModal
  },
  data() {
    return {
      filters: {
        keyword: '',
        status: ''
      },
      statusOptions: [
        { value: '', label: '全部' },
        { value: 'active', label: 'active' },
        { value: 'blocked', label: 'blocked' }
      ],
      users: [],
      page: 1,
      size: 18,
      total: 0,
      hasMore: true,
      loading: false,
      errorMsg: '',
      detailVisible: false,
      detailUser: null
    }
  },
  mounted() {
    this.reloadList()
  },
  methods: {
    formatDateTime(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString()
    },
    getInitial(name) {
      const safe = (name || '').trim()
      return safe ? safe[0].toUpperCase() : '?'
    },
    changeStatus(value) {
      if (this.filters.status === value) return
      this.filters.status = value
      this.reloadList()
    },
    async fetchUsers(reset) {
      if (this.loading) return
      this.loading = true
      this.errorMsg = ''

      const targetPage = reset ? 1 : this.page + 1

      try {
        const res = await getAdminUsers({
          page: targetPage,
          size: this.size,
          keyword: this.filters.keyword || undefined,
          status: this.filters.status || undefined
        })
        const data = (res && res.data && res.data.data) || {}
        const list = data.list || []

        this.users = reset ? list : this.users.concat(list)
        this.page = targetPage
        this.total = data.total || 0
        this.hasMore = Boolean(data.has_more)
      } catch (error) {
        this.errorMsg = resolveErrorMessage(error, '用户列表加载失败')
      } finally {
        this.loading = false
      }
    },
    reloadList() {
      this.fetchUsers(true)
    },
    loadMore() {
      if (!this.hasMore) return
      this.fetchUsers(false)
    },
    openDetail(item) {
      this.detailUser = item
      this.detailVisible = true
    },
    closeDetail() {
      this.detailVisible = false
      this.detailUser = null
    }
  }
}
</script>

<style scoped>
.page {
  height: 100%;
}

.page :deep(.panel) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page :deep(.panel-body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.filter-pill {
  min-height: 34px;
  border: 1px solid #d9dfd6;
  border-radius: 999px;
  padding: 0 12px;
  background: #fff;
  color: #344136;
  cursor: pointer;
}

.filter-pill.active {
  border-color: #93bc9a;
  background: #eef8ef;
  font-weight: 700;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  color: #677267;
  font-size: 13px;
}

.list-scroll {
  margin-top: 12px;
  height: calc(100% - 156px);
  min-height: 0;
  overflow-y: auto;
  padding-right: 6px;
}

.list-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid #e2e7df;
  border-radius: 18px;
  background: linear-gradient(180deg, #fff 0%, #fbfcfa 100%);
  cursor: pointer;
}

.list-row + .list-row {
  margin-top: 10px;
}

.list-row:hover {
  border-color: #bed0bf;
}

.row-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar,
.detail-avatar {
  width: 52px;
  height: 52px;
  border-radius: 999px;
  overflow: hidden;
  display: grid;
  place-items: center;
  background: #eef2ea;
  color: #3a4a3c;
  font-size: 18px;
  font-weight: 700;
}

.avatar img,
.detail-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-copy {
  min-width: 0;
}

.row-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.row-title {
  font-size: 16px;
  color: #203024;
}

.row-subline {
  margin: 8px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.row-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  color: #6b756b;
  font-size: 12px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-tag.is-active {
  background: #e5f4e8;
  color: #26693a;
}

.status-tag.is-blocked {
  background: #fce8ee;
  color: #ba3b5b;
}

.footer-row {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.ghost-btn {
  min-height: 40px;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #cfd4cc;
  background: #fff;
  color: #243027;
}

.ghost-btn[disabled] {
  cursor: not-allowed;
  opacity: 0.65;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
  color: #7b857b;
}

.detail-card {
  padding: 56px 24px 24px;
}

.detail-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.detail-kicker {
  margin: 0;
  color: #738073;
  font-size: 12px;
}

.detail-title {
  margin: 8px 0 0;
  font-size: 26px;
  color: #1e2b22;
}

.detail-subtitle {
  margin: 8px 0 0;
  color: #6f796f;
  font-size: 14px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 22px;
}

.info-card {
  border: 1px solid #e3e8df;
  border-radius: 16px;
  background: #f8faf7;
  padding: 12px 14px;
}

.info-label {
  display: block;
  color: #7a8479;
  font-size: 12px;
}

.info-card strong {
  display: block;
  margin-top: 6px;
  color: #223026;
}

.detail-time {
  margin: 18px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.error-text {
  color: #cf2e53;
}

@media (max-width: 980px) {
  .page {
    height: auto;
  }

  .list-scroll {
    height: auto;
    overflow: visible;
  }
}

@media (max-width: 640px) {
  .list-row {
    grid-template-columns: 1fr;
  }

  .row-stats {
    align-items: flex-start;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
