<template>
  <div class="empty-state">
    <p class="empty-title">{{ title }}</p>
    <p v-if="description" class="empty-description">{{ description }}</p>
    <slot />
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    title: {
      type: String,
      default: '暂无数据'
    },
    description: {
      type: String,
      default: ''
    }
  }
}
</script>

<style lang="scss" scoped>
.empty-state {
  border: 1px dashed #d7ddd2;
  border-radius: $radius-sm;
  padding: 22px 14px;
  text-align: center;
  color: #687067;
  background: #fcfcfa;
}

.empty-title {
  margin: 0;
  font-size: 14px;
}

.empty-description {
  margin: 8px 0 0;
  font-size: 12px;
  color: #8b938a;
}
</style>
