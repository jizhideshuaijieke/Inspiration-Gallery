<template>
  <section>
    <div v-if="loading" class="loading-wrap">正在加载通知...</div>
    <div v-else-if="items.length" class="timeline">
      <article v-for="item in items" :key="item.id" class="notice-item">
        <div class="item-top">
          <span class="type-badge" :class="`type-${item.type}`">{{ typeLabel(item.type) }}</span>
          <span class="item-time">{{ formatDateTime(item.created_at) }}</span>
        </div>
        <h4 class="item-title">{{ item.title }}</h4>
        <p class="item-body">{{ item.body }}</p>
        <button
          v-if="item.artwork_id"
          type="button"
          class="jump-btn"
          @click="$emit('open-artwork', item)"
        >
          {{ item.action_label || '查看作品' }}
        </button>
      </article>
    </div>
    <slot v-else name="empty" />
  </section>
</template>

<script>
const TYPE_LABEL_MAP = {
  comment: '评论',
  like: '点赞',
  admin: '站内通知'
}

export default {
  name: 'NoticeTimeline',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    items: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    typeLabel(type) {
      return TYPE_LABEL_MAP[type] || '消息'
    },
    formatDateTime(value) {
      if (!value) return ''
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleString()
    }
  }
}
</script>

<style lang="scss" scoped>
.loading-wrap {
  color: $color-muted;
  font-size: 13px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notice-item {
  @include panel-surface($radius: $radius-sm, $border: #e7ebe4, $background: #fff, $shadow: none);
  padding: 12px;
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.type-badge {
  border-radius: 9px;
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid transparent;
}

.type-comment {
  border-color: #bcd8ff;
  background: #eef6ff;
  color: #2b5b99;
}

.type-like {
  border-color: #ffd2dc;
  background: #fff0f4;
  color: #ad2f51;
}

.type-admin {
  border-color: #d9d9d9;
  background: #f5f5f5;
  color: #565656;
}

.item-time {
  color: #7f8780;
  font-size: 12px;
}

.item-title {
  margin: 8px 0 6px;
  font-size: 14px;
}

.item-body {
  margin: 0;
  color: #4d544d;
  font-size: 13px;
  line-height: 1.4;
}

.jump-btn {
  margin-top: 8px;
  padding: 6px 12px;
  font-size: 12px;
  @include ghost-button($height: 34px, $radius: 16px, $font-size: 12px);
}
</style>
