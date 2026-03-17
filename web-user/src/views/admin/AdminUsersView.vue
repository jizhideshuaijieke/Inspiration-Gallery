<template>
  <section class="page">
    <AdminPanel title="用户列表" subtitle="查看并处理用户状态">
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
                <span class="status-tag" :class="`is-${item.status}`">{{ formatStatus(item.status) }}</span>
              </div>
              <p class="row-subline">ID：{{ item.account_code || '-' }}</p>
            </div>
          </div>

          <div class="row-actions">
            <button
              v-if="item.status !== 'blocked'"
              type="button"
              class="danger-btn inline-btn"
              :disabled="actingUserId === item.id"
              @click.stop="blockUser(item)"
            >
              {{ actingUserId === item.id ? '处理中...' : '封禁' }}
            </button>
            <button
              v-else
              type="button"
              class="ghost-btn inline-btn"
              :disabled="actingUserId === item.id"
              @click.stop="unblockUser(item)"
            >
              {{ actingUserId === item.id ? '处理中...' : '解除封禁' }}
            </button>
          </div>
        </article>

        <div v-if="!loading && users.length === 0" class="empty-state">还没有用户</div>
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
            <p class="detail-kicker">ID：{{ detailUser.account_code || '-' }}</p>
            <h3 class="detail-title">{{ detailUser.username }}</h3>
            <p class="detail-subtitle">状态：{{ formatStatus(detailUser.status) }}</p>
          </div>
        </div>

        <p class="detail-time">创建时间：{{ formatDateTime(detailUser.created_at) }}</p>
        <p class="detail-time">更新时间：{{ formatDateTime(detailUser.updated_at) }}</p>

        <div class="detail-actions">
          <button
            v-if="detailUser.status !== 'blocked'"
            type="button"
            class="danger-btn"
            :disabled="actingUserId === detailUser.id"
            @click="blockUser(detailUser)"
          >
            {{ actingUserId === detailUser.id ? '处理中...' : '封禁账号' }}
          </button>
          <button
            v-else
            type="button"
            class="ghost-btn"
            :disabled="actingUserId === detailUser.id"
            @click="unblockUser(detailUser)"
          >
            {{ actingUserId === detailUser.id ? '处理中...' : '解除封禁' }}
          </button>
        </div>

        <p v-if="detailError" class="error-text detail-error">{{ detailError }}</p>
      </section>
    </AdminModal>
  </section>
</template>

<script>
import AdminPanel from '../../components/admin/AdminPanel.vue'
import AdminSearchBar from '../../components/admin/AdminSearchBar.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import { blockAdminUser, getAdminUsers, unblockAdminUser } from '../../api/admin'

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
        { value: 'active', label: '正常' },
        { value: 'blocked', label: '已封禁' }
      ],
      users: [],
      page: 1,
      size: 18,
      total: 0,
      hasMore: true,
      loading: false,
      errorMsg: '',
      detailVisible: false,
      detailUser: null,
      actingUserId: null,
      detailError: ''
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
    formatStatus(value) {
      const map = {
        active: '正常',
        blocked: '已封禁'
      }
      return map[value] || value || '-'
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
      this.detailError = ''
      this.detailUser = item
      this.detailVisible = true
    },
    closeDetail() {
      this.detailVisible = false
      this.detailUser = null
      this.detailError = ''
    },
    syncUserStatus(userId, status) {
      const index = this.users.findIndex((item) => item.id === userId)
      if (index < 0) return
      const nextUser = { ...this.users[index], status }
      this.$set(this.users, index, nextUser)
      if (this.detailUser && this.detailUser.id === userId) {
        this.detailUser = { ...this.detailUser, status }
      }
    },
    async blockUser(user) {
      if (!user || this.actingUserId) return

      this.actingUserId = user.id
      this.detailError = ''
      this.errorMsg = ''

      try {
        const res = await blockAdminUser(user.id)
        const data = (res && res.data && res.data.data) || {}
        this.syncUserStatus(user.id, data.status || 'blocked')
      } catch (error) {
        const message = resolveErrorMessage(error, '封禁失败')
        if (this.detailVisible && this.detailUser && this.detailUser.id === user.id) {
          this.detailError = message
        } else {
          this.errorMsg = message
        }
      } finally {
        this.actingUserId = null
      }
    },
    async unblockUser(user) {
      if (!user || this.actingUserId) return

      this.actingUserId = user.id
      this.detailError = ''
      this.errorMsg = ''

      try {
        const res = await unblockAdminUser(user.id)
        const data = (res && res.data && res.data.data) || {}
        this.syncUserStatus(user.id, data.status || 'active')
      } catch (error) {
        const message = resolveErrorMessage(error, '解除封禁失败')
        if (this.detailVisible && this.detailUser && this.detailUser.id === user.id) {
          this.detailError = message
        } else {
          this.errorMsg = message
        }
      } finally {
        this.actingUserId = null
      }
    }
  }
}
</script>

<style lang="scss" scoped>
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
  padding: 0 12px;
  color: #344136;
  @include ghost-button($height: 34px, $radius: 999px, $font-size: 13px);

  &.active {
    border-color: $color-primary-soft;
    background: #eef8ef;
    font-weight: 700;
  }
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
  @include panel-surface($radius: $radius-lg, $border: #e2e7df, $background: linear-gradient(180deg, #fff 0%, #fbfcfa 100%), $shadow: none);
  cursor: pointer;

  & + .list-row {
    margin-top: 10px;
  }

  &:hover {
    border-color: #bed0bf;
  }
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

.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.inline-btn {
  min-height: 34px;
  padding: 0 12px;
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

  &.is-active {
    background: $color-success-bg;
    color: $color-success-text;
  }

  &.is-blocked {
    background: $color-error-bg;
    color: #ba3b5b;
  }
}

.footer-row {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.ghost-btn {
  padding: 0 14px;
  @include ghost-button($height: 40px, $radius: $radius-md, $font-size: 13px);
}

.danger-btn {
  padding: 0 14px;
  @include danger-button($height: 40px, $radius: $radius-md, $font-size: 13px);
}

.blocked-tip {
  color: #b7425f;
  font-size: 12px;
  font-weight: 700;
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
  color: $color-text;
}

.detail-subtitle {
  margin: 8px 0 0;
  color: #6f796f;
  font-size: 14px;
}

.detail-time {
  margin: 18px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 18px;
}

.detail-error {
  margin-top: 12px;
}

.error-text {
  color: $color-error-text;
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

  .row-actions {
    justify-content: flex-start;
  }
}
</style>
