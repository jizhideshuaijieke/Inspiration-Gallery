<template>
  <section class="panel">
    <header v-if="title || subtitle || $slots.actions" class="panel-header">
      <div class="panel-title-wrap">
        <h3 v-if="title" class="panel-title">{{ title }}</h3>
        <p v-if="subtitle" class="panel-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="panel-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="panel-body">
      <slot />
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminPanel',
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
}
</script>

<style lang="scss" scoped>
.panel {
  @include panel-surface($radius: 20px, $border: var(--border-soft), $background: rgba(255, 255, 255, 0.94), $shadow: none);
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 16px 18px 14px;
  border-bottom: 1px solid #edf0ea;
}

.panel-title {
  margin: 0;
  font-size: 20px;
  color: $color-text;
}

.panel-subtitle {
  margin: 6px 0 0;
  color: $color-muted;
  font-size: 13px;
}

.panel-body {
  padding: 16px 18px 18px;
}
</style>
