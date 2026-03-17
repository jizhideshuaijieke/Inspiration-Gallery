<template>
  <div v-if="visible" class="detail-mask" @click.self="$emit('close')">
    <div class="detail-modal">
      <button type="button" class="close-btn" @click="$emit('close')">x</button>

      <div class="detail-image-wrap">
        <img v-if="detail && detail.result_image_url" class="detail-image" :src="detail.result_image_url"
          :alt="detail.title || 'artwork detail'" />
        <div v-else class="detail-empty">图片加载中...</div>
      </div>

      <section class="detail-side">
        <div v-if="detailLoading" class="detail-loading">详情加载中...</div>

        <div v-else-if="detail" class="detail-scroll">
          <header class="detail-head">
            <div class="detail-author-group">
              <button type="button" class="author-link" @click="$emit('open-author')">
                {{ detail.author && detail.author.username ? detail.author.username : '匿名作者' }}
              </button>
              <button
                v-if="canFollow"
                type="button"
                class="follow-chip"
                :class="{ active: followingAuthor }"
                :disabled="followLoading"
                @click="$emit('toggle-follow')"
              >
              {{ followLoading ? '处理中...' : followingAuthor ? '已关注' : '关注' }}
              </button>
            </div>
            <div class="detail-style">{{ detail.style && detail.style.name }}</div>
          </header>

          <div v-if="editableTitle" class="title-block">
            <div v-if="editingTitle" class="title-editor">
              <input
                v-model.trim="draftTitle"
                class="title-input"
                type="text"
                maxlength="100"
                placeholder="请输入作品标题"
              />
              <div class="title-editor-actions">
                <button
                  type="button"
                  class="ghost-btn"
                  :disabled="titleSaving || !canSubmitTitle"
                  @click="submitTitle"
                >
                  保存标题
                </button>
                <button
                  type="button"
                  class="ghost-btn"
                  :disabled="titleSaving"
                  @click="cancelTitleEdit"
                >
                  取消
                </button>
              </div>
            </div>
            <div v-else class="title-row">
              <h3 class="detail-title">{{ detail.title || '未命名作品' }}</h3>
              <button type="button" class="link-btn" @click="startTitleEdit">修改标题</button>
            </div>
          </div>
          <h3 v-else class="detail-title">{{ detail.title || '未命名作品' }}</h3>
          <p class="detail-time">{{ formatDateTime(detail.created_at) }}</p>
          <p v-if="canManage && detail.visibility === 'hidden'" class="status-tip">
            作品已下架，目前仅在你的仓库中可见。
          </p>

          <div class="detail-actions">
            <button type="button" class="ghost-btn" :disabled="likeLoading" @click="$emit('toggle-like')">
              {{ liked ? '取消点赞' : '点赞' }} · {{ detail.like_count || 0 }}
            </button>
            <button
              v-if="canManage && detail.visibility !== 'hall' && detail.visibility !== 'hidden'"
              type="button"
              class="ghost-btn"
              :disabled="manageLoading"
              @click="$emit('publish')"
            >
              发布到大厅
            </button>
            <button
              v-if="canManage && detail.visibility === 'hall'"
              type="button"
              class="ghost-btn"
              :disabled="manageLoading"
              @click="$emit('recall')"
            >
              撤回到仓库
            </button>
            <button
              v-if="canManage"
              type="button"
              class="ghost-btn danger-btn"
              :disabled="manageLoading"
              @click="$emit('delete')"
            >
              删除作品
            </button>
          </div>

          <p v-if="detailError" class="error-text">{{ detailError }}</p>

          <h4 class="comment-title">评论（{{ detail.comment_count || 0 }}）</h4>
          <div class="comment-list">
            <p v-if="commentLoading" class="comment-empty">评论加载中...</p>
            <p v-else-if="comments.length === 0" class="comment-empty">还没有人评论</p>
            <article v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-user">
                {{ comment.user && comment.user.username ? comment.user.username : '用户' }}
              </div>
              <p class="comment-content">{{ comment.content }}</p>
              <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
            </article>
          </div>

          <form class="comment-form" @submit.prevent="onSubmit">
            <input v-model.trim="draftComment" class="comment-input" type="text" maxlength="200"
              placeholder="写下你的评论" />
            <button type="submit" class="ghost-btn" :disabled="commentPosting">发送</button>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArtworkDetail',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    detail: {
      type: Object,
      default: null
    },
    detailLoading: {
      type: Boolean,
      default: false
    },
    detailError: {
      type: String,
      default: ''
    },
    comments: {
      type: Array,
      default: () => []
    },
    commentLoading: {
      type: Boolean,
      default: false
    },
    commentPosting: {
      type: Boolean,
      default: false
    },
    liked: {
      type: Boolean,
      default: false
    },
    likeLoading: {
      type: Boolean,
      default: false
    },
    canFollow: {
      type: Boolean,
      default: false
    },
    followingAuthor: {
      type: Boolean,
      default: false
    },
    followLoading: {
      type: Boolean,
      default: false
    },
    canManage: {
      type: Boolean,
      default: false
    },
    editableTitle: {
      type: Boolean,
      default: false
    },
    titleSaving: {
      type: Boolean,
      default: false
    },
    manageLoading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      draftComment: '',
      draftTitle: '',
      editingTitle: false
    }
  },
  computed: {
    canSubmitTitle() {
      const nextTitle = (this.draftTitle || '').trim()
      const currentTitle = (this.detail && this.detail.title ? this.detail.title : '').trim()
      return Boolean(nextTitle) && nextTitle !== currentTitle
    }
  },
  watch: {
    visible(next) {
      if (!next) {
        this.draftComment = ''
        this.editingTitle = false
        this.draftTitle = this.detail && this.detail.title ? this.detail.title : ''
      }
    },
    detail: {
      immediate: true,
      handler(next) {
        this.draftTitle = next && next.title ? next.title : ''
      }
    },
    titleSaving(next, prev) {
      if (!next && prev && this.detail && this.draftTitle === this.detail.title) {
        this.editingTitle = false
      }
    }
  },
  methods: {
    formatDateTime(value) {
      if (!value) return ''
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString()
    },
    onSubmit() {
      if (!this.draftComment) return
      this.$emit('submit-comment', this.draftComment)
      this.draftComment = ''
    },
    startTitleEdit() {
      this.editingTitle = true
      this.draftTitle = this.detail && this.detail.title ? this.detail.title : ''
    },
    cancelTitleEdit() {
      this.editingTitle = false
      this.draftTitle = this.detail && this.detail.title ? this.detail.title : ''
    },
    submitTitle() {
      if (!this.canSubmitTitle || this.titleSaving) return
      this.$emit('save-title', this.draftTitle.trim())
    }
  }
}
</script>

<style lang="scss" scoped>
.detail-mask {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(32, 35, 32, 0.4);
  display: grid;
  place-items: center;
  padding: 18px;
}

.detail-modal {
  width: min(1200px, 95vw);
  height: min(88vh, 860px);
  background: #fff;
  border-radius: $radius-lg;
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  overflow: hidden;
  position: relative;
  box-shadow: $shadow-large;
}

.close-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 17px;
  background: rgba(35, 35, 35, 0.4);
  color: #fff;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
}

.detail-image-wrap {
  background: #f4f4f4;
  display: grid;
  place-items: center;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-empty {
  color: #8a8f89;
}

.detail-side {
  border-left: 1px solid #eceeea;
  display: flex;
  flex-direction: column;
  padding: 22px 18px 14px;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.detail-scroll {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.detail-loading {
  color: #666e66;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.detail-author-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.author-link {
  border: 0;
  background: transparent;
  padding: 0;
  color: #223024;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  text-align: left;
}

.follow-chip {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  white-space: nowrap;
  @include ghost-button($height: 30px, $radius: 999px, $font-size: 12px);

  &.active {
    border-color: #afcbb2;
    background: #eef7ef;
    color: $color-primary;
  }
}

.detail-style {
  font-size: 12px;
  color: #6e756e;
}

.detail-title {
  margin: 12px 0 6px;
  font-size: 20px;
}

.title-block {
  margin-top: 12px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.title-row .detail-title {
  margin: 0;
}

.title-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-input {
  min-height: 38px;
  @include input-shell($height: 38px, $radius: 16px, $padding-x: 12px);
}

.title-editor-actions {
  display: flex;
  gap: 8px;
}

.link-btn {
  border: 0;
  background: transparent;
  color: #2f6b48;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
}

.detail-time {
  margin: 0 0 10px;
  color: #7e857d;
  font-size: 12px;
}

.status-tip {
  margin: 0 0 12px;
  border-radius: 10px;
  padding: 8px 10px;
  background: #f7f1f1;
  color: #8a4453;
  font-size: 12px;
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.ghost-btn {
  padding: 8px 14px;
  font-size: 13px;
  text-decoration: none;
  @include ghost-button($height: 38px, $radius: 18px, $font-size: 13px);
}

.danger-btn {
  border-color: #f0c7cf;
  color: #a23a55;
}

.comment-title {
  margin: 6px 0 10px;
  font-size: 14px;
}

.comment-list {
  flex: 1;
  min-height: 140px;
  border: 1px solid #ebede8;
  border-radius: 10px;
  padding: 8px;
  overflow: auto;
  background: #fafbf8;
}

.comment-empty {
  margin: 6px 0;
  color: #838b82;
  font-size: 13px;
}

.comment-item {
  padding: 8px 6px;
  border-bottom: 1px solid #edf0ea;
}

.comment-item:last-child {
  border-bottom: 0;
}

.comment-user {
  font-size: 13px;
  font-weight: 600;
}

.comment-content {
  margin: 4px 0;
  line-height: 1.35;
  font-size: 13px;
}

.comment-time {
  color: #808981;
  font-size: 12px;
}

.comment-form {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  position: sticky;
  bottom: 0;
  background: #fff;
  padding-top: 10px;
}

.comment-input {
  flex: 1;
  min-width: 0;
  @include input-shell($height: 34px, $radius: 16px, $padding-x: 12px);
}

.error-text {
  color: $color-error-text;
}

@media (max-width: 1200px) {
  .detail-modal {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 900px) {
  .detail-modal {
    width: 96vw;
    height: 92vh;
    grid-template-columns: 1fr;
    grid-template-rows: 44vh 1fr;
  }

  .detail-side {
    border-left: 0;
    border-top: 1px solid #eceeea;
  }

  .title-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
