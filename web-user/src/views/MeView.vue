<template>
  <section class="me-page">
    <PagePanel class="profile-panel" :title="pageTitle">
      <template #actions>
        <button v-if="isOwnProfile" type="button" class="ghost-btn" @click="startEditProfile">
          编辑资料
        </button>
      </template>

      <template v-if="userId">
        <div class="profile-head">
          <div class="avatar">
            <img
              v-if="profile && profile.avatar_url"
              class="avatar-img"
              :src="profile.avatar_url"
              alt="avatar"
            />
            <span v-else>{{ profileInitial }}</span>
          </div>
          <div class="profile-text">
            <h3 class="username">{{ profile ? profile.username : '加载中...' }}</h3>
            <div class="account-row">
              <span class="account-label">用户ID</span>
              <code class="account-code">{{ profileAccountCode }}</code>
            </div>
          </div>
        </div>

        <StatGrid :items="statsItems" />
      </template>

      <EmptyState
        v-else
        title="尚未登录"
        description="登录后可查看个人主页。"
      >
        <button type="button" class="ghost-btn" @click="$router.push('/login')">去登录</button>
      </EmptyState>
    </PagePanel>

    <PagePanel v-if="userId" class="artwork-panel" :title="artworkPanelTitle">
      <div class="artwork-scroll">
        <HallMasonry
          :feed="artworks"
          :loading="loadingArtworks"
          :has-more="artworksHasMore"
          @load-more="loadMoreArtworks"
          @open-detail="openDetail"
        >
          <template #card-footer="{ item }">
            <span>❤ {{ item.like_count || 0 }}</span>
            <span>💬 {{ item.comment_count || 0 }}</span>
            <span class="meta-tag">{{ visibilityLabel(item.visibility) }}</span>
          </template>
        </HallMasonry>
      </div>
    </PagePanel>

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
      :editable-title="canManageDetail"
      :title-saving="titleSaving"
      :manage-loading="manageLoading"
      @close="closeDetail"
      @open-author="openAuthorProfile"
      @toggle-follow="toggleFollowAuthor"
      @toggle-like="toggleLike"
      @submit-comment="submitComment"
      @save-title="saveArtworkTitle"
      @publish="publishArtwork"
      @recall="recallArtwork"
      @delete="removeArtwork"
    />

    <ProfileEditModal
      :visible="profileEditVisible"
      :profile="profile"
      :saving="savingProfile"
      :submit-error="profileSaveError"
      @close="closeProfileEditor"
      @submit="handleProfileSubmit"
    />

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
  </section>
</template>

<script>
import { getCurrentUserIdFromToken } from '../utils/auth'
import {
  followUser,
  getUserArtworks,
  getUserProfile,
  unfollowUser,
  updateMyProfile,
  uploadMyAvatar
} from '../api/users'
import {
  getArtworkComments,
  getArtworkDetail,
  updateArtwork,
  deleteArtwork,
  likeArtwork,
  postArtworkComment,
  unlikeArtwork
} from '../api/artworks'
import { createArtworkCommentSocket } from '../utils/artworkCommentSocket'
import PagePanel from '../components/common/PagePanel.vue'
import StatGrid from '../components/common/StatGrid.vue'
import EmptyState from '../components/common/EmptyState.vue'
import HallMasonry from '../components/hall/HallMasonry.vue'
import ArtworkDetail from '../components/hall/ArtworkDetail.vue'
import ProfileEditModal from '../components/profile/ProfileEditModal.vue'

const VISIBILITY_LABEL_MAP = {
  private: '私密',
  profile: '主页公开',
  hall: '大厅公开',
  hidden: '已下架'
}

function getErrorMessage(error, fallback) {
  const data = error && error.response && error.response.data
  if (data && data.message) return data.message

  const detail = data && data.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0]
    if (first && first.msg) return first.msg
  }

  return fallback
}

export default {
  name: 'MeView',
  components: {
    PagePanel,
    StatGrid,
    EmptyState,
    HallMasonry,
    ArtworkDetail,
    ProfileEditModal
  },
  data() {
    return {
      userId: null,
      currentUserId: null,
      profile: null,
      artworks: [],
      artworksPage: 1,
      artworksSize: 12,
      artworksHasMore: true,
      loadingArtworks: false,
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
      titleSaving: false,
      manageLoading: false,
      profileEditVisible: false,
      savingProfile: false,
      profileSaveError: '',
      errorMsg: ''
    }
  },
  computed: {
    isOwnProfile() {
      return Boolean(this.currentUserId && this.userId === this.currentUserId)
    },
    pageTitle() {
      return this.isOwnProfile ? '我的主页' : '用户主页'
    },
    artworkPanelTitle() {
      return this.isOwnProfile ? '我的仓库' : '公开作品'
    },
    profileInitial() {
      return this.getNameInitial(this.profile && this.profile.username)
    },
    profileAccountCode() {
      return (this.profile && this.profile.account_code) || '-'
    },
    statsItems() {
      const stats = (this.profile && this.profile.stats) || {}
      return [
        { key: 'artworks', label: '作品', value: stats.artworks_count || 0 },
        { key: 'likes', label: '获赞', value: stats.likes_received || 0 },
        { key: 'followers', label: '粉丝', value: stats.followers_count || 0 },
        { key: 'following', label: '关注', value: stats.following_count || 0 }
      ]
    },
    canManageDetail() {
      if (!this.detail || !this.currentUserId) return false
      return this.detail.author && this.detail.author.id === this.currentUserId
    },
    canFollowAuthor() {
      if (!this.detail || !this.detail.author || !this.detail.author.id) return false
      return Boolean(this.currentUserId && this.detail.author.id !== this.currentUserId)
    }
  },
  watch: {
    '$route.params.userId'() {
      this.syncViewedUserId()
      this.reloadAll()
    },
    '$route.query.artwork'() {
      this.maybeOpenArtworkFromRoute()
    }
  },
  methods: {
    syncViewedUserId() {
      const routeUserId = Number(this.$route.params.userId)
      if (Number.isInteger(routeUserId) && routeUserId > 0) {
        this.userId = routeUserId
        return
      }

      this.userId = this.currentUserId
    },
    getNameInitial(name) {
      const safeName = (name || '').trim()
      if (!safeName) return '?'
      return safeName[0].toUpperCase()
    },
    visibilityLabel(value) {
      return VISIBILITY_LABEL_MAP[value] || value || '未知'
    },
    startEditProfile() {
      if (!this.profile) return
      this.profileSaveError = ''
      this.profileEditVisible = true
    },
    closeProfileEditor() {
      this.profileEditVisible = false
      this.profileSaveError = ''
    },
    async handleProfileSubmit(payload) {
      if (this.savingProfile) return
      this.savingProfile = true
      this.profileSaveError = ''

      try {
        let avatarUrl = (this.profile && this.profile.avatar_url) || null

        if (payload && payload.avatarFile) {
          const uploadRes = await uploadMyAvatar(payload.avatarFile)
          const uploadData = (uploadRes && uploadRes.data && uploadRes.data.data) || {}
          if (!uploadData.avatar_url) {
            throw new Error('头像上传失败')
          }
          avatarUrl = uploadData.avatar_url
        }

        const res = await updateMyProfile({
          username: (payload && payload.username) || null,
          avatar_url: avatarUrl
        })
        const data = (res && res.data && res.data.data) || {}
        this.profile = { ...this.profile, ...data }
        this.closeProfileEditor()
      } catch (error) {
        this.profileSaveError = getErrorMessage(error, '资料更新失败')
      } finally {
        this.savingProfile = false
      }
    },
    async loadProfile() {
      const res = await getUserProfile(this.userId)
      this.profile = res && res.data && res.data.data
    },
    async loadArtworks(reset) {
      if (this.loadingArtworks) return
      this.loadingArtworks = true
      const targetPage = reset ? 1 : this.artworksPage + 1

      try {
        const res = await getUserArtworks(this.userId, {
          page: targetPage,
          size: this.artworksSize
        })
        const data = (res && res.data && res.data.data) || {}
        const list = data.list || []
        this.artworks = reset ? list : this.artworks.concat(list)
        this.artworksPage = targetPage
        this.artworksHasMore = Boolean(data.has_more)
      } finally {
        this.loadingArtworks = false
      }
    },
    async loadMoreArtworks() {
      if (!this.artworksHasMore) return
      try {
        await this.loadArtworks(false)
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '加载作品失败')
      }
    },
    async reloadAll() {
      this.errorMsg = ''
      this.profile = null
      this.artworks = []
      this.artworksPage = 1
      this.artworksHasMore = true
      if (!this.userId) return

      try {
        await Promise.all([this.loadProfile(), this.loadArtworks(true)])
        this.maybeOpenArtworkFromRoute()
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '个人页加载失败')
      }
    },
    clearArtworkQuery() {
      if (!this.$route.query.artwork) return
      this.$router.replace({ path: this.$route.path, query: {} }).catch(() => {})
    },
    maybeOpenArtworkFromRoute() {
      if (!this.userId || this.detailVisible) return
      const artworkId = Number(this.$route.query.artwork)
      if (!Number.isInteger(artworkId) || artworkId <= 0) return
      this.openDetail(artworkId)
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
    disconnectCommentSocket() {
      if (!this.commentSocket) return
      this.commentSocket.close()
      this.commentSocket = null
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
        this.syncArtworkStat(this.detail.id, { comment_count: nextCount })
      } catch (error) {
        if (!silent) {
          this.detailError = getErrorMessage(error, '评论加载失败')
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
        this.comments =
          (commentsRes &&
            commentsRes.data &&
            commentsRes.data.data &&
            commentsRes.data.data.list) ||
          []
        const total =
          commentsRes &&
          commentsRes.data &&
          commentsRes.data.data &&
          typeof commentsRes.data.data.total === 'number'
            ? commentsRes.data.data.total
            : this.detail && this.detail.comment_count
        if (this.detail && typeof total === 'number') {
          this.detail = { ...this.detail, comment_count: total }
          this.syncArtworkStat(this.detail.id, { comment_count: total })
        }
        await this.refreshAuthorFollowState(
          this.detail && this.detail.author ? this.detail.author.id : null
        )
        this.connectCommentSocket(artworkId)
      } catch (error) {
        this.detailError = getErrorMessage(error, '详情加载失败')
      } finally {
        this.detailLoading = false
        this.commentLoading = false
      }
    },
    syncArtworkStat(artworkId, patch) {
      const index = this.artworks.findIndex((item) => item.id === artworkId)
      if (index < 0) return
      this.$set(this.artworks, index, { ...this.artworks[index], ...patch })
    },
    async saveArtworkTitle(title) {
      if (!this.detail || this.titleSaving) return
      this.titleSaving = true
      this.detailError = ''

      try {
        const res = await updateArtwork(this.detail.id, { title })
        const payload = (res && res.data && res.data.data) || {}
        const nextTitle = payload.title || title
        this.detail = { ...this.detail, title: nextTitle }
        this.syncArtworkStat(this.detail.id, { title: nextTitle })
      } catch (error) {
        this.detailError = getErrorMessage(error, '标题修改失败')
      } finally {
        this.titleSaving = false
      }
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
        this.syncArtworkStat(this.detail.id, { like_count: likeCount })
      } catch (error) {
        this.detailError = getErrorMessage(error, '点赞操作失败')
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
        this.detailError = getErrorMessage(error, '关注操作失败')
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
        this.detailError = getErrorMessage(error, '评论发送失败')
      } finally {
        this.commentPosting = false
      }
    },
    async publishArtwork() {
      if (!this.detail || this.manageLoading) return
      this.manageLoading = true
      this.detailError = ''

      try {
        await updateArtwork(this.detail.id, { visibility: 'hall' })
        this.detail = { ...this.detail, visibility: 'hall' }
        this.syncArtworkStat(this.detail.id, { visibility: 'hall' })
      } catch (error) {
        this.detailError = getErrorMessage(error, '发布失败')
      } finally {
        this.manageLoading = false
      }
    },
    async recallArtwork() {
      if (!this.detail || this.manageLoading) return
      this.manageLoading = true
      this.detailError = ''

      try {
        await updateArtwork(this.detail.id, { visibility: 'private' })
        this.detail = { ...this.detail, visibility: 'private' }
        this.syncArtworkStat(this.detail.id, { visibility: 'private' })
      } catch (error) {
        this.detailError = getErrorMessage(error, '撤回失败')
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
        this.artworks = this.artworks.filter((item) => item.id !== this.detail.id)
        if (this.profile && this.profile.stats) {
          const nextCount = Math.max((this.profile.stats.artworks_count || 1) - 1, 0)
          this.profile = { ...this.profile, stats: { ...this.profile.stats, artworks_count: nextCount } }
        }
        this.closeDetail()
      } catch (error) {
        this.detailError = getErrorMessage(error, '删除失败')
      } finally {
        this.manageLoading = false
      }
    }
  },
  mounted() {
    this.currentUserId = getCurrentUserIdFromToken()
    this.syncViewedUserId()
    this.reloadAll()
  },
  beforeDestroy() {
    this.disconnectCommentSocket()
  }
}
</script>

<style lang="scss" scoped>
.me-page {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

:deep(.me-page .panel) {
  margin-bottom: 0;
}

.profile-panel {
  flex-shrink: 0;
}

.artwork-panel {
  flex: 1;
  min-height: 0;
}

:deep(.artwork-panel) {
  display: flex;
  flex-direction: column;
}

:deep(.artwork-panel .panel-body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.artwork-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 8px;
}

.ghost-btn {
  padding: 6px 12px;
  font-size: 12px;
  @include ghost-button($height: 36px, $radius: 16px, $font-size: 12px);
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 28px;
  display: grid;
  place-items: center;
  background: #eef2ea;
  color: #3a4a3c;
  font-size: 20px;
  font-weight: 700;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  margin: 0;
  font-size: 20px;
  color: $color-text;
}

.profile-text {
  min-width: 0;
}

.account-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 6px 10px;
  border: 1px solid #dce3d8;
  border-radius: 999px;
  background: #f6f8f4;
}

.account-label {
  color: $color-muted;
  font-size: 12px;
}

.account-code {
  padding: 0;
  background: transparent;
  color: #243027;
  font-size: 12px;
  font-family: 'Consolas', 'Courier New', monospace;
}

.meta-tag {
  border: 1px solid #d6dbd3;
  border-radius: 10px;
  padding: 2px 8px;
  color: #516051;
  font-size: 11px;
}

.error-text {
  margin: 0;
  flex-shrink: 0;
  color: $color-error-text;
}

@media (max-width: 900px) {
  .me-page {
    height: auto;
    overflow: visible;
  }

  .artwork-panel {
    flex: none;
  }

  .artwork-scroll {
    overflow: visible;
    padding-right: 0;
  }
}
</style>
