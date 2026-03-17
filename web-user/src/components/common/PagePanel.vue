<template>
  <section class="panel">
    <header v-if="hasHeader" class="panel-header">
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
  name: 'PagePanel',
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    }
  },
  computed: {
    hasHeader() {
      return Boolean(this.title || this.subtitle || this.$slots.actions)
    }
  }
}
</script>

<style lang="scss" scoped>
.panel {
  @include panel-surface($radius: $radius-lg, $border: var(--border-soft), $background: #fff, $shadow: none);
  margin-bottom: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid #edf0ea;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
}

.panel-subtitle {
  margin: 6px 0 0;
  color: $color-muted;
  font-size: 13px;
}

.panel-actions {
  flex-shrink: 0;
}

.panel-body {
  padding: 14px 16px;
}
</style>
