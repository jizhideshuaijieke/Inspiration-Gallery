<template>
  <section class="hall-page">
    <header class="topbar">
      <input
        v-model.trim="keyword"
        class="search-input"
        type="text"
        placeholder="搜索标题 / 作者 / 风格"
      />
      <button type="button" class="avatar-btn" @click="goToProfile">
        <img
          v-if="currentUserProfile && currentUserProfile.avatar_url"
          class="avatar-image"
          :src="currentUserProfile.avatar_url"
          alt="profile avatar"
        />
        <span v-else class="avatar-fallback">{{ currentUserInitial }}</span>
      </button>
    </header>

    <div class="status-line">
      <span>最新作品流</span>
      <span v-if="loadingFeed">加载中...</span>
      <span v-else-if="feedError" class="error-text">{{ feedError }}</span>
    </div>

    <div class="feed-scroll">
      <HallMasonry
        :feed="filteredFeed"
        :loading="loadingFeed"
        :has-more="hasMore"
        @open-detail="openDetail"
        @load-more="loadMore"
      />
    </div>

    <ArtworkDetail
      :visible="detailVisible"
      :detail="detail"
      :detail-loading="detailLoading"
      :detail-error="detailError"
      :comments="comments"
      :comment-loading="commentLoading"
      :comment-posting="commentPosting"
      :liked="liked"
      :like-loading="likeLoading"
      :can-follow="canFollowAuthor"
      :following-author="followingAuthor"
      :follow-loading="followLoading"
      :can-manage="canManageDetail"
      :manage-loading="manageLoading"
      @close="closeDetail"
      @open-author="openAuthorProfile"
      @toggle-follow="toggleFollowAuthor"
      @toggle-like="toggleLike"
      @submit-comment="submitComment"
      @recall="recallArtwork"
      @delete="removeArtwork"
    />
  </section>
</template>

<script>
import { getHallFeed } from '../api/hall'
import {
  deleteArtwork,
  getArtworkComments,
  getArtworkDetail,
  likeArtwork,
  postArtworkComment,
  unlikeArtwork,
  updateArtwork
} from '../api/artworks'
import { followUser, getUserProfile, unfollowUser } from '../api/users'
import { getCurrentUserIdFromToken } from '../utils/auth'
import { createArtworkCommentSocket } from '../utils/artworkCommentSocket'
import HallMasonry from '../components/hall/HallMasonry.vue'
import ArtworkDetail from '../components/hall/ArtworkDetail.vue'

function resolveErrorMessage(error, fallback) {
  return (
    (error &&
      error.response &&
      error.response.data &&
      error.response.data.message) ||
    fallback
  )
}

export default {
  name: 'HallView',
  components: {
    HallMasonry,
    ArtworkDetail
  },
  data() {
    return {
      keyword: '',
      feed: [],
      page: 1,
      size: 21,
      hasMore: true,
      loadingFeed: false,
      feedError: '',
      detailVisible: false,
      detailLoading: false,
      detailError: '',
      detail: null,
      comments: [],
      commentLoading: false,
      commentPosting: false,
      commentSocket: null,
      liked: false,
      likeLoading: false,
      followingAuthor: false,
      followLoading: false,
      manageLoading: false,
      currentUserId: null,
      currentUserProfile: null
    }
  },
  computed: {
    filteredFeed() {
      const query = (this.keyword || '').toLowerCase()
      if (!query) return this.feed
      return this.feed.filter((item) => {
        const title = (item.title || '').toLowerCase()
        const author = ((item.author && item.author.username) || '').toLowerCase()
        const style = ((item.style && item.style.name) || '').toLowerCase()
        return title.includes(query) || author.includes(query) || style.includes(query)
      })
    },
    canManageDetail() {
      if (!this.detail || !this.currentUserId) return false
      return this.detail.author && this.detail.author.id === this.currentUserId
    },
    canFollowAuthor() {
      if (!this.detail || !this.detail.author || !this.detail.author.id) return false
      return Boolean(this.currentUserId && this.detail.author.id !== this.currentUserId)
    },
    currentUserInitial() {
      const username = (this.currentUserProfile && this.currentUserProfile.username) || ''
      return username ? username[0].toUpperCase() : '我'
    }
  },
  watch: {
    '$route.query.artwork'() {
      this.maybeOpenArtworkFromRoute()
    }
  },
  methods: {
    async fetchFeed(reset) {
      if (this.loadingFeed) return

      const targetPage = reset ? 1 : this.page + 1
      this.loadingFeed = true
      this.feedError = ''

      try {
        const res = await getHallFeed({ page: targetPage, size: this.size })
        const data = (res && res.data && res.data.data) || {}
        const list = data.list || []

        this.feed = reset ? list : this.feed.concat(list)
        this.page = targetPage
        this.hasMore = Boolean(data.has_more)
      } catch (error) {
        this.feedError = resolveErrorMessage(error, '加载失败，请检查后端是否启动')
      } finally {
        this.loadingFeed = false
      }
    },
    async loadMore() {
      if (!this.hasMore) return
      await this.fetchFeed(false)
    },
    async loadCurrentUserProfile() {
      if (!this.currentUserId) {
        this.currentUserProfile = null
        return
      }

      try {
        const res = await getUserProfile(this.currentUserId)
        this.currentUserProfile = (res && res.data && res.data.data) || null
      } catch (_) {
        this.currentUserProfile = null
      }
    },
    goToProfile() {
      this.$router.push(this.currentUserId ? '/me' : '/login')
    },
    clearArtworkQuery() {
      if (!this.$route.query.artwork) return
      this.$router.replace({ path: this.$route.path, query: {} }).catch(() => {})
    },
    maybeOpenArtworkFromRoute() {
      if (this.detailVisible) return
      const artworkId = Number(this.$route.query.artwork)
      if (!Number.isInteger(artworkId) || artworkId <= 0) return
      this.openDetail(artworkId)
    },
    disconnectCommentSocket() {
      if (!this.commentSocket) return
      this.commentSocket.close()
      this.commentSocket = null
    },
    closeDetail() {
      this.disconnectCommentSocket()
      this.detailVisible = false
      this.detailError = ''
      this.detail = null
      this.comments = []
      this.followingAuthor = false
      this.followLoading = false
      this.clearArtworkQuery()
    },
    connectCommentSocket(artworkId) {
      this.disconnectCommentSocket()
      if (!artworkId) return

      const token = localStorage.getItem('token') || ''
      const socket = createArtworkCommentSocket(artworkId, {
        token,
        onMessage: (payload) => {
          if (!payload || payload.type !== 'artwork_comments_refresh') return
          if (!this.detail || this.detail.id !== artworkId) return
          this.refreshDetailComments({
            silent: true,
            countHint:
              typeof payload.comment_count === 'number' ? payload.comment_count : null
          })
        },
        onClose: () => {
          if (this.commentSocket === socket) this.commentSocket = null
        },
        onError: () => {
          if (this.commentSocket === socket) this.commentSocket = null
        }
      })

      this.commentSocket = socket
    },
    async refreshDetailComments({ silent = false, countHint = null } = {}) {
      if (!this.detail) return
      if (!silent) this.commentLoading = true

      try {
        const commentsRes = await getArtworkComments(this.detail.id, { page: 1, size: 30 })
        const data = (commentsRes && commentsRes.data && commentsRes.data.data) || {}
        this.comments = data.list || []

        const nextCount =
          typeof countHint === 'number'
            ? countHint
            : typeof data.total === 'number'
              ? data.total
              : this.detail.comment_count || 0

        this.detail = { ...this.detail, comment_count: nextCount }
        this.syncFeedStat(this.detail.id, { comment_count: nextCount })
      } catch (error) {
        if (!silent) {
          this.detailError = resolveErrorMessage(error, '评论加载失败')
        }
      } finally {
        if (!silent) this.commentLoading = false
      }
    },
    openAuthorProfile() {
      if (!this.detail || !this.detail.author || !this.detail.author.id) return
      const authorId = this.detail.author.id
      this.closeDetail()
      this.$router.push(authorId === this.currentUserId ? '/me' : `/users/${authorId}`)
    },
    async refreshAuthorFollowState(authorId) {
      if (!this.currentUserId || !authorId || authorId === this.currentUserId) {
        this.followingAuthor = false
        return
      }

      try {
        const res = await getUserProfile(authorId)
        const data = (res && res.data && res.data.data) || {}
        this.followingAuthor = Boolean(data.is_following)
      } catch (_) {
        this.followingAuthor = false
      }
    },
    async openDetail(artworkId) {
      this.detailVisible = true
      this.detailLoading = true
      this.commentLoading = true
      this.detailError = ''
      this.detail = null
      this.comments = []
      this.liked = false
      this.followingAuthor = false

      try {
        const [detailRes, commentsRes] = await Promise.all([
          getArtworkDetail(artworkId),
          getArtworkComments(artworkId, { page: 1, size: 30 })
        ])
        this.detail = detailRes && detailRes.data && detailRes.data.data

        const commentsData = (commentsRes && commentsRes.data && commentsRes.data.data) || {}
        this.comments = commentsData.list || []

        const total =
          typeof commentsData.total === 'number'
            ? commentsData.total
            : this.detail && this.detail.comment_count
        if (this.detail && typeof total === 'number') {
          this.detail = { ...this.detail, comment_count: total }
          this.syncFeedStat(this.detail.id, { comment_count: total })
        }

        await this.refreshAuthorFollowState(
          this.detail && this.detail.author ? this.detail.author.id : null
        )
        this.connectCommentSocket(artworkId)
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '详情加载失败')
      } finally {
        this.detailLoading = false
        this.commentLoading = false
      }
    },
    syncFeedStat(artworkId, patch) {
      const index = this.feed.findIndex((item) => item.id === artworkId)
      if (index < 0) return
      this.$set(this.feed, index, { ...this.feed[index], ...patch })
    },
    async toggleLike() {
      if (!this.detail || this.likeLoading) return
      if (!localStorage.getItem('token')) {
        this.detailError = '请先登录后再点赞'
        return
      }

      this.likeLoading = true
      this.detailError = ''

      try {
        const res = this.liked
          ? await unlikeArtwork(this.detail.id)
          : await likeArtwork(this.detail.id)
        const payload = res && res.data && res.data.data
        const likeCount = payload && payload.like_count

        this.liked = !this.liked
        this.detail = { ...this.detail, like_count: likeCount }
        this.syncFeedStat(this.detail.id, { like_count: likeCount })
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '点赞操作失败')
      } finally {
        this.likeLoading = false
      }
    },
    async toggleFollowAuthor() {
      if (!this.detail || !this.detail.author || !this.detail.author.id || this.followLoading) return
      if (!localStorage.getItem('token')) {
        this.$router.push('/login')
        return
      }

      const authorId = this.detail.author.id
      if (authorId === this.currentUserId) return

      this.followLoading = true
      this.detailError = ''

      try {
        if (this.followingAuthor) {
          await unfollowUser(authorId)
          this.followingAuthor = false
        } else {
          await followUser(authorId)
          this.followingAuthor = true
        }
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '关注操作失败')
      } finally {
        this.followLoading = false
      }
    },
    async submitComment(content) {
      if (!this.detail || this.commentPosting) return
      if (!localStorage.getItem('token')) {
        this.detailError = '请先登录后再评论'
        return
      }
      if (!content) return

      this.commentPosting = true
      this.detailError = ''

      try {
        await postArtworkComment(this.detail.id, { content, parent_id: null })
        await this.refreshDetailComments({
          countHint: (this.detail.comment_count || 0) + 1
        })
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '评论发送失败')
      } finally {
        this.commentPosting = false
      }
    },
    async recallArtwork() {
      if (!this.detail || this.manageLoading) return
      this.manageLoading = true
      this.detailError = ''

      try {
        await updateArtwork(this.detail.id, { visibility: 'private' })
        this.feed = this.feed.filter((item) => item.id !== this.detail.id)
        this.closeDetail()
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '撤回失败')
      } finally {
        this.manageLoading = false
      }
    },
    async removeArtwork() {
      if (!this.detail || this.manageLoading) return
      this.manageLoading = true
      this.detailError = ''

      try {
        await deleteArtwork(this.detail.id)
        this.feed = this.feed.filter((item) => item.id !== this.detail.id)
        this.closeDetail()
      } catch (error) {
        this.detailError = resolveErrorMessage(error, '删除失败')
      } finally {
        this.manageLoading = false
      }
    }
  },
  mounted() {
    this.currentUserId = getCurrentUserIdFromToken()
    this.loadCurrentUserProfile()
    this.fetchFeed(true)
    this.maybeOpenArtworkFromRoute()
  },
  beforeDestroy() {
    this.disconnectCommentSocket()
  }
}
</script>

<style scoped lang="scss">
.hall-page {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 58px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 160px;
  @include input-shell(40px, 20px, 16px);
  background: #f0f1ee;
}

.avatar-btn {
  width: 44px;
  height: 44px;
  border: 1px solid $color-border-strong;
  background: $color-surface;
  border-radius: 50%;
  padding: 0;
  cursor: pointer;
  overflow: hidden;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: #eef2ea;
  color: #314137;
  font-size: 15px;
  font-weight: 700;
}

.status-line {
  display: flex;
  justify-content: space-between;
  color: $color-muted;
  font-size: 13px;
  margin-bottom: 14px;
  flex-shrink: 0;
}

.feed-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 8px;
}

.error-text {
  color: $color-error-text;
}

@media (max-width: 900px) {
  .hall-page {
    height: auto;
    overflow: visible;
  }

  .feed-scroll {
    overflow: visible;
    padding-right: 0;
  }
}
</style>
