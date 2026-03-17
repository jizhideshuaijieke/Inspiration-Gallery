<template>
  <section class="hall-list">
    <div class="feed-grid">
      <article v-for="item in feed" :key="item.id" class="art-card" @click="$emit('open-detail', item.id)">
        <img class="art-cover" :src="item.result_image_url" :alt="item.title || 'artwork'" loading="lazy" />
        <h3 class="art-title">{{ item.title || '未命名作品' }}</h3>
        <div v-if="item.author || item.style" class="art-meta">
          <span v-if="item.author && item.author.username" class="author">
            {{ item.author.username }}
          </span>
          <span v-if="item.style && item.style.name" class="style-tag">
            {{ item.style.name }}
          </span>
        </div>
        <div class="art-stats">
          <slot name="card-footer" :item="item">
            <span>❤ {{ item.like_count || 0 }}</span>
            <span>💬 {{ item.comment_count || 0 }}</span>
          </slot>
        </div>
      </article>
    </div>

    <div class="load-row">
      <button v-if="hasMore && !loading" type="button" class="ghost-btn" @click="$emit('load-more')">
        加载更多
      </button>
      <span v-else-if="loading">加载中...</span>
      <span v-else-if="!hasMore && feed.length > 0">已经到底了</span>
      <span v-else>还没有作品</span>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HallMasonry',
  props: {
    feed: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    hasMore: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.ghost-btn {
  padding: 8px 14px;
  font-size: 13px;
  text-decoration: none;
  @include ghost-button($height: 38px, $radius: 18px, $font-size: 13px);
}

.feed-grid {
  column-count: 3;
  column-gap: 16px;
}

.art-card {
  width: 100%;
  break-inside: avoid;
  @include panel-surface($radius: 16px, $border: var(--border-soft), $background: #fff, $shadow: none);
  margin-bottom: 16px;
  padding: 10px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.art-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(30, 40, 31, 0.08);
}

.art-cover {
  width: 100%;
  border-radius: 12px;
  display: block;
  background: #f1f1f1;
}

.art-title {
  margin: 10px 2px 6px;
  font-size: 15px;
  line-height: 1.35;
  color: $color-text;
}

.art-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #4c554d;
  font-size: 12px;
}

.style-tag {
  border: 1px solid #d8ddd5;
  border-radius: 10px;
  padding: 2px 6px;
  color: #667266;
}

.art-stats {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  color: #798379;
  font-size: 12px;
}

.load-row {
  margin: 8px 0 24px;
  text-align: center;
  color: $color-muted;
}

@media (max-width: 1200px) {
  .feed-grid {
    column-count: 2;
  }
}

@media (max-width: 900px) {
  .feed-grid {
    column-count: 1;
  }
}
</style>
