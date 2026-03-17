<template>
  <div class="stats-grid">
    <article v-for="item in items" :key="item.key" class="stat-card">
      <p class="stat-label">{{ item.label }}</p>
      <p class="stat-value">{{ item.value }}</p>
    </article>
  </div>
</template>

<script>
export default {
  name: 'StatGrid',
  props: {
    items: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style lang="scss" scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.stat-card {
  @include panel-surface($radius: $radius-sm, $border: #e8ebe4, $background: #fafbf8, $shadow: none);
  padding: 10px;
}

.stat-label {
  margin: 0 0 6px;
  font-size: 12px;
  color: $color-muted;
}

.stat-value {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
