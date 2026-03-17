<template>
  <section class="page">
    <AdminPanel title="作品管理" subtitle="使用管理员接口查看大厅作品并执行下架">
      <AdminSearchBar v-model="filters.keyword" placeholder="搜索作品标题">
        <button type="button" class="ghost-btn" @click="reloadList">搜索</button>
      </AdminSearchBar>

      <div class="filter-row">
        <button
          v-for="option in visibilityOptions"
          :key="option.value"
          type="button"
          class="filter-pill"
          :class="{ active: filters.visibility === option.value }"
          @click="changeVisibility(option.value)"
        >
          {{ option.label }}
        </button>
      </div>

      <div class="meta-row">
        <span>共 {{ total }} 条</span>
        <span v-if="loading">加载中...</span>
        <span v-else-if="errorMsg" class="error-text">{{ errorMsg }}</span>
      </div>

      <div class="list-scroll">
        <article
          v-for="item in artworks"
          :key="item.id"
          class="list-row"
          @click="openDetail(item)"
        >
          <div class="row-main">
            <div class="row-top">
              <strong class="row-title">{{ item.title || '未命名作品' }}</strong>
              <span class="status-tag" :class="`is-${item.visibility}`">{{ visibilityLabel(item.visibility) }}</span>
            </div>
            <p class="row-subline">
              #{{ item.id }} · 作者 {{ item.author && item.author.username ? item.author.username : '-' }} ·
              风格 {{ item.style && item.style.name ? item.style.name : '-' }}
            </p>
          </div>
          <div class="row-stats">
            <span>赞 {{ item.like_count || 0 }}</span>
            <span>评 {{ item.comment_count || 0 }}</span>
            <span>{{ formatDateTime(item.created_at) }}</span>
          </div>
        </article>

        <div v-if="!loading && artworks.length === 0" class="empty-state">暂无作品数据</div>
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
      <div class="detail-shell">
        <div class="detail-image-wrap">
          <img
            v-if="detailData && detailData.result_image_url"
            class="detail-image"
            :src="detailData.result_image_url"
            :alt="detailData.title || 'artwork detail'"
          />
          <div v-else class="detail-empty">{{ detailLoading ? '详情加载中...' : '暂无图片' }}</div>
        </div>

        <section class="detail-side">
          <div v-if="detailLoading" class="detail-loading">正在加载作品详情...</div>
          <template v-else-if="detailData">
            <div class="detail-head">
              <div>
                <p class="detail-kicker">作品 #{{ detailData.id }}</p>
                <h3 class="detail-title">{{ detailData.title || '未命名作品' }}</h3>
              </div>
              <span class="status-tag" :class="`is-${detailData.visibility}`">
                {{ visibilityLabel(detailData.visibility) }}
              </span>
            </div>

            <div class="detail-grid">
              <article class="info-card">
                <span class="info-label">作者</span>
                <strong>{{ detailData.author && detailData.author.username ? detailData.author.username : '-' }}</strong>
              </article>
              <article class="info-card">
                <span class="info-label">风格</span>
                <strong>{{ detailData.style && detailData.style.name ? detailData.style.name : '-' }}</strong>
              </article>
              <article class="info-card">
                <span class="info-label">点赞</span>
                <strong>{{ detailData.like_count || 0 }}</strong>
              </article>
              <article class="info-card">
                <span class="info-label">评论</span>
                <strong>{{ detailData.comment_count || 0 }}</strong>
              </article>
            </div>

            <p class="detail-time">创建时间：{{ formatDateTime(detailData.created_at) }}</p>

            <div class="reason-box">
              <label class="field-label" for="hide-reason">下架原因</label>
              <textarea
                id="hide-reason"
                v-model.trim="hideReason"
                class="reason-input"
                maxlength="200"
                placeholder="请输入下架原因"
              ></textarea>
            </div>

            <div class="detail-actions">
              <button
                type="button"
                class="danger-btn"
                :disabled="actionLoading || detailData.visibility === 'hidden'"
                @click="submitHide"
              >
                {{ actionLoading ? '处理中...' : '下架作品' }}
              </button>
              <a
                v-if="detailData.result_image_url"
                class="ghost-btn"
                :href="detailData.result_image_url"
                target="_blank"
                rel="noopener noreferrer"
              >
                打开原图
              </a>
            </div>

            <p v-if="detailError" class="error-text detail-error">{{ detailError }}</p>

            <div class="comment-block">
              <h4>最新评论</h4>
              <div class="comment-list">
                <p v-if="commentLoading" class="detail-muted">评论加载中...</p>
                <p v-else-if="comments.length === 0" class="detail-muted">暂无评论</p>
                <article v-for="comment in comments" :key="comment.id" class="comment-item">
                  <div class="comment-top">
                    <strong>{{ comment.user && comment.user.username ? comment.user.username : '用户' }}</strong>
                    <span>{{ formatDateTime(comment.created_at) }}</span>
                  </div>
                  <p>{{ comment.content }}</p>
                </article>
              </div>
            </div>
          </template>
        </section>
      </div>
    </AdminModal>
  </section>
</template>

<script>
import AdminPanel from '../components/AdminPanel.vue'
import AdminSearchBar from '../components/AdminSearchBar.vue'
import AdminModal from '../components/AdminModal.vue'
import { getAdminArtworks, hideAdminArtwork } from '../api/admin'
import { getArtworkComments, getArtworkDetail } from '../api/artworks'

function resolveErrorMessage(error, fallback) {
  return (
    (error && error.response && error.response.data && error.response.data.message) ||
    fallback
  )
}

export default {
  name: 'AdminArtworksView',
  components: {
    AdminPanel,
    AdminSearchBar,
    AdminModal
  },
  data() {
    return {
      filters: {
        keyword: '',
        visibility: ''
      },
      visibilityOptions: [
        { value: '', label: '全部' },
        { value: 'hall', label: '大厅中' },
        { value: 'hidden', label: '已下架' },
        { value: 'profile', label: '主页公开' },
        { value: 'private', label: '私密' }
      ],
      artworks: [],
      page: 1,
      size: 18,
      total: 0,
      hasMore: true,
      loading: false,
      errorMsg: '',
      detailVisible: false,
      detailLoading: false,
      detailData: null,
      comments: [],
      commentLoading: false,
      detailError: '',
      actionLoading: false,
      hideReason: ''
    }
  },
  mounted() {
    this.reloadList()
  },
  methods: {
    visibilityLabel(value) {
      const map = {
        hall: '大厅中',
        hidden: '已下架',
        profile: '主页公开',
        private: '私密'
      }
      return map[value] || value || '未知'
    },
    formatDateTime(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString()
    },
    changeVisibility(value) {
      if (this.filters.visibility === value) return
      this.filters.visibility = value
      this.reloadList()
    },
    async fetchList(reset) {
      if (this.loading) return
      this.loading = true
      this.errorMsg = ''

      const targetPage = reset ? 1 : this.page + 1

      try {
        const res = await getAdminArtworks({
          page: targetPage,
          size: this.size,
          visibility: this.filters.visibility || undefined,
          keyword: this.filters.keyword || undefined
        })
        const data = (res && res.data && res.data.data) || {}
        const list = data.list || []

        this.artworks = reset ? list : this.artworks.concat(list)
        this.page = targetPage
        this.total = data.total || 0
        this.hasMore = Boolean(data.has_more)
      } catch (error) {
        this.errorMsg = resolveErrorMessage(error, '作品列表加载失败')
      } finally {
        this.loading = false
      }
    },
    reloadList() {
      this.fetchList(true)
    },
    loadMore() {
      if (!this.hasMore) return
      this.fetchList(false)
    },
    async openDetail(item) {
      this.detailVisible = true
      this.detailLoading = true
      this.commentLoading = true
      this.detailError = ''
      this.hideReason = ''
      this.detailData = null
      this.comments = []

      try {
        const [detailRes, commentsRes] = await Promise.all([
          getArtworkDetail(item.id),
          getArtworkComments(item.id, { page: 1, size: 20 })
        ])
        this.detailData = (detailRes && detailRes.data && detailRes.data.data) || item
        this.comments =
          (commentsRes &&
            commentsRes.data &&
            commentsRes.data.data &&
            commentsRes.data.data.list) ||
          []
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '作品详情加载失败')
      } finally {
        this.detailLoading = false
        this.commentLoading = false
      }
    },
    closeDetail() {
      this.detailVisible = false
      this.detailLoading = false
      this.commentLoading = false
      this.detailData = null
      this.comments = []
      this.detailError = ''
      this.hideReason = ''
      this.actionLoading = false
    },
    async submitHide() {
      if (!this.detailData || this.actionLoading) return
      if (!this.hideReason) {
        this.detailError = '请输入下架原因'
        return
      }

      this.actionLoading = true
      this.detailError = ''

      try {
        const res = await hideAdminArtwork(this.detailData.id, { reason: this.hideReason })
        const data = (res && res.data && res.data.data) || {}
        this.detailData = { ...this.detailData, visibility: data.visibility || 'hidden' }

        const index = this.artworks.findIndex((item) => item.id === this.detailData.id)
        if (index >= 0) {
          this.$set(this.artworks, index, {
            ...this.artworks[index],
            visibility: data.visibility || 'hidden'
          })
        }
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '下架失败')
      } finally {
        this.actionLoading = false
      }
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

.status-tag.is-hall {
  background: #e5f4e8;
  color: #26693a;
}

.status-tag.is-hidden {
  background: #fce8ee;
  color: #ba3b5b;
}

.status-tag.is-private,
.status-tag.is-profile {
  background: #eef1ec;
  color: #556056;
}

.footer-row {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.ghost-btn,
.danger-btn {
  min-height: 40px;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 13px;
  cursor: pointer;
}

.ghost-btn {
  border: 1px solid #cfd4cc;
  background: #fff;
  color: #243027;
}

.danger-btn {
  border: 0;
  background: #b7425f;
  color: #fff;
}

.ghost-btn[disabled],
.danger-btn[disabled] {
  cursor: not-allowed;
  opacity: 0.65;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
  color: #7b857b;
}

.detail-shell {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  max-height: 90vh;
}

.detail-image-wrap {
  min-height: 640px;
  background: #f2f4f1;
  display: grid;
  place-items: center;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-empty,
.detail-loading,
.detail-muted {
  color: #7e877e;
}

.detail-side {
  border-left: 1px solid #eceeea;
  padding: 24px 20px 20px;
  overflow-y: auto;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.detail-kicker {
  margin: 0;
  color: #738073;
  font-size: 12px;
}

.detail-title {
  margin: 8px 0 0;
  font-size: 24px;
  color: #1e2b22;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
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
  margin: 16px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.reason-box {
  margin-top: 18px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  color: #4d594e;
  font-size: 13px;
}

.reason-input {
  width: 100%;
  min-height: 92px;
  border: 1px solid #d8ddd5;
  border-radius: 16px;
  padding: 12px 14px;
  resize: vertical;
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.detail-error {
  margin-top: 12px;
}

.comment-block {
  margin-top: 22px;
}

.comment-block h4 {
  margin: 0 0 12px;
  color: #1f2b22;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-item {
  border: 1px solid #e2e7df;
  border-radius: 16px;
  padding: 12px 14px;
  background: #fbfcfa;
}

.comment-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: #667267;
  font-size: 12px;
}

.comment-item p {
  margin: 8px 0 0;
  color: #233024;
  line-height: 1.6;
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

  .detail-shell {
    grid-template-columns: 1fr;
  }

  .detail-image-wrap {
    min-height: 320px;
  }

  .detail-side {
    border-left: 0;
    border-top: 1px solid #eceeea;
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

  .detail-actions {
    flex-direction: column;
  }
}
</style>
