<template>
  <section class="page">
    <AdminPanel title="评论管理" subtitle="查看并处理作品评论">
      <AdminSearchBar v-model="keyword" placeholder="搜索评论内容 / 用户名 / 作品标题">
        <button type="button" class="ghost-btn" @click="reloadList">刷新</button>
      </AdminSearchBar>

      <div class="filter-row">
        <button
          v-for="option in visibilityOptions"
          :key="option.value"
          type="button"
          class="filter-pill"
          :class="{ active: artworkVisibility === option.value }"
          @click="changeVisibility(option.value)"
        >
          {{ option.label }}
        </button>
      </div>

      <div class="meta-row">
        <span>共 {{ comments.length }} 条评论</span>
        <span v-if="loading">加载中...</span>
        <span v-else-if="errorMsg" class="error-text">{{ errorMsg }}</span>
      </div>

      <div class="list-scroll">
        <article
          v-for="item in filteredComments"
          :key="item.id"
          class="list-row"
          @click="openDetail(item)"
        >
          <div class="row-main">
            <div class="row-top">
              <strong class="row-title">评论</strong>
              <span class="status-tag">{{ item.artworkVisibilityLabel }}</span>
            </div>
            <p class="row-content">{{ item.content }}</p>
            <p class="row-subline">
              ID：{{ item.id }} · {{ item.username }} · 作品《{{ item.artworkTitle }}》 · 作品ID：{{ item.artworkId }}
            </p>
          </div>
          <div class="row-stats">
            <span>{{ formatDateTime(item.createdAt) }}</span>
          </div>
        </article>

        <div v-if="!loading && filteredComments.length === 0" class="empty-state">还没有评论</div>
      </div>

      <div class="footer-row">
        <button
          type="button"
          class="ghost-btn"
          :disabled="loading || !hasMoreArtworks"
          @click="loadMore"
        >
          {{ hasMoreArtworks ? '加载更多' : '没有更多了' }}
        </button>
      </div>
    </AdminPanel>

    <AdminModal :visible="detailVisible" @close="closeDetail">
      <div class="detail-shell">
        <div class="detail-image-wrap">
          <img
            v-if="detailArtwork && detailArtwork.result_image_url"
            class="detail-image"
            :src="detailArtwork.result_image_url"
            :alt="detailArtwork.title || 'artwork detail'"
          />
          <div v-else class="detail-empty">{{ detailLoading ? '详情加载中...' : '暂无作品图片' }}</div>
        </div>

        <section class="detail-side">
          <div v-if="detailComment">
            <p class="detail-kicker">ID：{{ detailComment.id }}</p>
            <h3 class="detail-title">{{ detailComment.username }}</h3>
            <p class="detail-time">{{ formatDateTime(detailComment.createdAt) }}</p>

            <article class="content-card">
              <span class="info-label">评论内容</span>
              <p>{{ detailComment.content }}</p>
            </article>

            <div class="detail-grid">
              <article class="info-card">
                <span class="info-label">所属作品</span>
                <strong>{{ detailComment.artworkTitle }}</strong>
              </article>
              <article class="info-card">
                <span class="info-label">作品ID</span>
                <strong>{{ detailComment.artworkId }}</strong>
              </article>
            </div>

            <div class="reason-box">
              <label class="field-label" for="delete-reason">处理说明</label>
              <textarea
                id="delete-reason"
                v-model.trim="deleteReason"
                class="reason-input"
                maxlength="200"
                placeholder="选填"
              ></textarea>
            </div>

            <div class="detail-actions">
              <button
                type="button"
                class="danger-btn"
                :disabled="actionLoading"
                @click="submitDelete"
              >
                {{ actionLoading ? '处理中...' : '删除评论' }}
              </button>
              <button type="button" class="ghost-btn" @click="closeDetail">关闭</button>
            </div>

            <p v-if="detailError" class="error-text detail-error">{{ detailError }}</p>
          </div>
        </section>
      </div>
    </AdminModal>
  </section>
</template>

<script>
import AdminPanel from '../../components/admin/AdminPanel.vue'
import AdminSearchBar from '../../components/admin/AdminSearchBar.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import { getAdminArtworks, deleteAdminComment } from '../../api/admin'
import { getArtworkComments, getArtworkDetail } from '../../api/artworks'

function resolveErrorMessage(error, fallback) {
  return (
    (error && error.response && error.response.data && error.response.data.message) ||
    fallback
  )
}

export default {
  name: 'AdminCommentsView',
  components: {
    AdminPanel,
    AdminSearchBar,
    AdminModal
  },
  data() {
    return {
      keyword: '',
      artworkVisibility: 'hall',
      visibilityOptions: [
        { value: 'hall', label: '大厅作品' },
        { value: 'hidden', label: '已下架作品' },
        { value: '', label: '全部作品' }
      ],
      comments: [],
      artworkPage: 1,
      artworkSize: 10,
      hasMoreArtworks: true,
      loading: false,
      errorMsg: '',
      detailVisible: false,
      detailLoading: false,
      detailComment: null,
      detailArtwork: null,
      deleteReason: '',
      detailError: '',
      actionLoading: false
    }
  },
  computed: {
    filteredComments() {
      const query = (this.keyword || '').trim().toLowerCase()
      if (!query) return this.comments

      return this.comments.filter((item) => {
        return (
          (item.content || '').toLowerCase().includes(query) ||
          (item.username || '').toLowerCase().includes(query) ||
          (item.artworkTitle || '').toLowerCase().includes(query)
        )
      })
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
    visibilityLabel(value) {
      const map = {
        hall: '大厅作品',
        hidden: '已下架作品',
        profile: '主页公开',
        private: '私密作品'
      }
      return map[value] || '作品'
    },
    changeVisibility(value) {
      if (this.artworkVisibility === value) return
      this.artworkVisibility = value
      this.reloadList()
    },
    async fetchComments(reset) {
      if (this.loading) return
      this.loading = true
      this.errorMsg = ''

      const targetPage = reset ? 1 : this.artworkPage + 1

      try {
        const artworkRes = await getAdminArtworks({
          page: targetPage,
          size: this.artworkSize,
          visibility: this.artworkVisibility || undefined
        })
        const artworkData = (artworkRes && artworkRes.data && artworkRes.data.data) || {}
        const artworks = artworkData.list || []

        const commentGroups = await Promise.all(
          artworks.map(async (artwork) => {
            try {
              const commentsRes = await getArtworkComments(artwork.id, { page: 1, size: 50 })
              const list =
                (commentsRes &&
                  commentsRes.data &&
                  commentsRes.data.data &&
                  commentsRes.data.data.list) ||
                []

              return list.map((comment) => ({
                id: comment.id,
                content: comment.content,
                username: (comment.user && comment.user.username) || '用户',
                createdAt: comment.created_at,
                artworkId: artwork.id,
                artworkTitle: artwork.title || '未命名作品',
                artworkVisibility: artwork.visibility,
                artworkVisibilityLabel: this.visibilityLabel(artwork.visibility)
              }))
            } catch (_) {
              return []
            }
          })
        )

        const merged = commentGroups.flat().sort((a, b) => {
          const timeA = new Date(a.createdAt || 0).getTime()
          const timeB = new Date(b.createdAt || 0).getTime()
          return timeB - timeA
        })

        this.comments = reset ? merged : this.comments.concat(merged)
        this.artworkPage = targetPage
        this.hasMoreArtworks = Boolean(artworkData.has_more)
      } catch (error) {
        this.errorMsg = resolveErrorMessage(error, '评论列表加载失败')
      } finally {
        this.loading = false
      }
    },
    reloadList() {
      this.comments = []
      this.artworkPage = 1
      this.hasMoreArtworks = true
      this.fetchComments(true)
    },
    loadMore() {
      if (!this.hasMoreArtworks) return
      this.fetchComments(false)
    },
    async openDetail(item) {
      this.detailVisible = true
      this.detailLoading = true
      this.detailComment = item
      this.detailArtwork = null
      this.deleteReason = ''
      this.detailError = ''

      try {
        const res = await getArtworkDetail(item.artworkId)
        this.detailArtwork = (res && res.data && res.data.data) || null
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '作品详情加载失败')
      } finally {
        this.detailLoading = false
      }
    },
    closeDetail() {
      this.detailVisible = false
      this.detailLoading = false
      this.detailComment = null
      this.detailArtwork = null
      this.deleteReason = ''
      this.detailError = ''
      this.actionLoading = false
    },
    async submitDelete() {
      if (!this.detailComment || this.actionLoading) return
      this.actionLoading = true
      this.detailError = ''

      try {
        await deleteAdminComment(this.detailComment.id, {
          reason: this.deleteReason || undefined
        })
        this.comments = this.comments.filter((item) => item.id !== this.detailComment.id)
        this.closeDetail()
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '删除评论失败')
      } finally {
        this.actionLoading = false
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

.row-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.row-title {
  font-size: 16px;
  color: #203024;
}

.row-content {
  margin: 8px 0 0;
  color: #233024;
  line-height: 1.6;
}

.row-subline {
  margin: 8px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.row-stats {
  color: #6b756b;
  font-size: 12px;
  white-space: nowrap;
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
  padding: 0 14px;
}

.ghost-btn {
  @include ghost-button($height: 40px, $radius: $radius-md, $font-size: 13px);
}

.danger-btn {
  @include danger-button($height: 40px, $radius: $radius-md, $font-size: 13px);
}

.empty-state {
  padding: 40px 0;
  text-align: center;
  color: #7b857b;
}

.detail-shell {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  max-height: 90vh;
}

.detail-image-wrap {
  min-height: 620px;
  background: #f2f4f1;
  display: grid;
  place-items: center;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-empty {
  color: #7e877e;
}

.detail-side {
  border-left: 1px solid #eceeea;
  padding: 24px 20px 20px;
  overflow-y: auto;
}

.detail-kicker {
  margin: 0;
  color: #738073;
  font-size: 12px;
}

.detail-title {
  margin: 8px 0 0;
  font-size: 24px;
  color: $color-text;
}

.detail-time {
  margin: 12px 0 0;
  color: #6f796f;
  font-size: 13px;
}

.content-card {
  margin-top: 18px;
  @include panel-surface($radius: $radius-lg, $border: #e3e8df, $background: #f8faf7, $shadow: none);
  padding: 14px 16px;
}

.content-card p {
  margin: 10px 0 0;
  color: #243027;
  line-height: 1.7;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.info-card {
  @include panel-surface($radius: 16px, $border: #e3e8df, $background: #fff, $shadow: none);
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

.reason-box {
  margin-top: 18px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  color: $color-text-soft;
  font-size: 13px;
}

.reason-input {
  width: 100%;
  min-height: 92px;
  border: 1px solid #d8ddd5;
  border-radius: 16px;
  padding: 12px 14px;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: $color-primary-soft;
    box-shadow: 0 0 0 3px rgba(147, 188, 154, 0.12);
  }
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
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

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-actions {
    flex-direction: column;
  }
}
</style>
