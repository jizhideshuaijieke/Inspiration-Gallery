<template>
  <header class="toolbar">
    <input
      :value="value"
      class="search-input"
      type="text"
      :placeholder="placeholder"
      @input="$emit('input', $event.target.value)"
    />
    <div class="toolbar-actions">
      <slot />
    </div>
  </header>
</template>

<script>
export default {
  name: 'AdminSearchBar',
  props: {
    value: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '搜索'
    }
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  flex: 1;
  min-width: 0;
  height: 48px;
  border: 1px solid #dbe1d8;
  border-radius: 18px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.86);
  font-size: 14px;
  color: #213024;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 720px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-actions {
    justify-content: flex-end;
  }
}
</style>
