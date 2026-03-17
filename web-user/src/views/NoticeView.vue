<template>
  <section class="notice-page">
    <PagePanel title="通知" subtitle="作品动态">
      <template #actions>
        <button
          v-if="userId"
          type="button"
          class="ghost-btn"
          @click="reloadNotices"
        >
          刷新
        </button>
      </template>

      <NoticeTimeline
        v-if="userId"
        :loading="loading"
        :items="noticeItems"
        @open-artwork="openArtworkFromNotice"
      >
        <template #empty>
          <EmptyState title="暂无通知" description="有新的点赞、评论或处理通知时，会显示在这里。" />
        </template>
      </NoticeTimeline>

      <EmptyState
        v-else
        title="尚未登录"
        description="登录后可查看作品相关通知。"
      >
        <button type="button" class="ghost-btn" @click="$router.push('/login')">去登录</button>
      </EmptyState>
    </PagePanel>

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
  </section>
</template>

<script>
import { getCurrentUserIdFromToken } from '../utils/auth'
import { getArtworkComments } from '../api/artworks'
import { getMyNotices, getUserArtworks } from '../api/users'
import { createNoticeSocket } from '../utils/noticeSocket'
import PagePanel from '../components/common/PagePanel.vue'
import EmptyState from '../components/common/EmptyState.vue'
import NoticeTimeline from '../components/notice/NoticeTimeline.vue'

function getErrorMessage(error, fallback) {
  return (
    (error &&
      error.response &&
      error.response.data &&
      error.response.data.message) ||
    fallback
  )
}

function safeTime(value) {
  const timestamp = new Date(value).getTime()
  return Number.isFinite(timestamp) ? timestamp : 0
}

export default {
  name: 'NoticeView',
  components: {
    PagePanel,
    EmptyState,
    NoticeTimeline
  },
  data() {
    return {
      userId: null,
      loading: false,
      errorMsg: '',
      noticeItems: [],
      noticeSocket: null,
      noticeSocketMuted: false,
      noticeReloadTimer: null
    }
  },
  methods: {
    async buildNoticeItems() {
      const [artworksRes, adminNoticesRes] = await Promise.all([
        getUserArtworks(this.userId, { page: 1, size: 8 }),
        getMyNotices({ page: 1, size: 20 })
      ])
      const artworks =
        (artworksRes &&
          artworksRes.data &&
          artworksRes.data.data &&
          artworksRes.data.data.list) ||
        []
      const adminItems =
        (adminNoticesRes &&
          adminNoticesRes.data &&
          adminNoticesRes.data.data &&
          adminNoticesRes.data.data.list) ||
        []

      const commentGroupResults = await Promise.all(
        artworks.map(async (artwork) => {
          try {
            const commentsRes = await getArtworkComments(artwork.id, { page: 1, size: 5 })
            const list =
              (commentsRes &&
                commentsRes.data &&
                commentsRes.data.data &&
                commentsRes.data.data.list) ||
              []
            return { artwork, comments: list }
          } catch (_) {
            return { artwork, comments: [] }
          }
        })
      )

      const commentItems = commentGroupResults.flatMap((group) =>
        group.comments.map((comment) => ({
          id: `comment-${comment.id}`,
          type: 'comment',
          title: `${(comment.user && comment.user.username) || '用户'} 评论了《${group.artwork.title || '未命名作品'}》`,
          body: `《${group.artwork.title || '未命名作品'}》：${comment.content}`,
          created_at: comment.created_at,
          artwork_id: group.artwork.id,
          action_label: '查看作品',
          target_view: 'hall'
        }))
      )

      const likeItems = artworks
        .filter((artwork) => (artwork.like_count || 0) > 0)
        .map((artwork) => ({
          id: `like-${artwork.id}`,
          type: 'like',
          title: `《${artwork.title || '未命名作品'}》新增 ${artwork.like_count} 个赞`,
          body: '去看看最近的互动吧。',
          created_at: artwork.created_at,
          artwork_id: artwork.id,
          action_label: '查看作品',
          target_view: 'hall'
        }))

      const allItems = commentItems.concat(likeItems).concat(adminItems)
      allItems.sort((a, b) => safeTime(b.created_at) - safeTime(a.created_at))
      this.noticeItems = allItems
    },
    async reloadNotices() {
      if (!this.userId) return
      this.loading = true
      this.errorMsg = ''

      try {
        await this.buildNoticeItems()
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '通知加载失败')
      } finally {
        this.loading = false
      }
    },
    scheduleNoticeReload() {
      if (this.noticeReloadTimer) {
        clearTimeout(this.noticeReloadTimer)
      }

      this.noticeReloadTimer = setTimeout(() => {
        this.noticeReloadTimer = null
        this.reloadNotices()
      }, 250)
    },
    connectNoticeSocket() {
      if (!this.userId || this.noticeSocket || typeof WebSocket === 'undefined') return

      const socket = createNoticeSocket({
        token: localStorage.getItem('token'),
        onMessage: this.handleNoticeSocketMessage,
        onClose: this.handleNoticeSocketClose,
        onError: this.handleNoticeSocketError
      })

      if (!socket) return

      this.noticeSocket = socket
      this.noticeSocketMuted = false
    },
    disconnectNoticeSocket() {
      if (!this.noticeSocket) {
        this.noticeSocketMuted = false
        return
      }

      const socket = this.noticeSocket
      this.noticeSocketMuted = true
      this.noticeSocket = null
      socket.close()
    },
    handleNoticeSocketMessage(payload) {
      if (!payload || payload.type === 'connected') return
      if (payload.type === 'notice_refresh') {
        this.scheduleNoticeReload()
      }
    },
    handleNoticeSocketError() {
      // Reconnect is handled in the close callback.
    },
    handleNoticeSocketClose() {
      const muted = this.noticeSocketMuted
      this.noticeSocket = null
      this.noticeSocketMuted = false

      if (!muted && this.userId) {
        setTimeout(() => {
          if (!this.noticeSocket && this.userId) {
            this.connectNoticeSocket()
          }
        }, 1200)
      }
    },
    openArtworkFromNotice(item) {
      if (!item || !item.artwork_id) {
        return
      }

      if (item.target_view === 'me') {
        this.$router.push({
          path: '/me',
          query: { artwork: String(item.artwork_id) }
        })
        return
      }

      this.$router.push({
        path: '/hall',
        query: { artwork: String(item.artwork_id) }
      })
    }
  },
  mounted() {
    this.userId = getCurrentUserIdFromToken()
    this.reloadNotices()
    this.connectNoticeSocket()
  },
  activated() {
    this.connectNoticeSocket()
  },
  deactivated() {
    this.disconnectNoticeSocket()
  },
  beforeDestroy() {
    this.disconnectNoticeSocket()
    if (this.noticeReloadTimer) {
      clearTimeout(this.noticeReloadTimer)
      this.noticeReloadTimer = null
    }
  }
}
</script>

<style lang="scss" scoped>
.notice-page {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.ghost-btn {
  padding: 6px 12px;
  font-size: 12px;
  @include ghost-button($height: 36px, $radius: 16px, $font-size: 12px);
}

.error-text {
  margin: 0;
  color: $color-error-text;
  font-size: 13px;
}

@media (max-width: 900px) {
  .notice-page {
    height: auto;
    overflow: visible;
    padding-right: 0;
  }
}
</style>
