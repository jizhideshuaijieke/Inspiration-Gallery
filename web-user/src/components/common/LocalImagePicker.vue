<template>
  <div class="picker">
    <input
      ref="fileInput"
      class="picker-input"
      type="file"
      :accept="accept"
      :disabled="disabled"
      @change="onPickFile"
    />
    <button type="button" class="ghost-btn" :disabled="disabled" @click="triggerPick">
      {{ buttonText }}
    </button>
    <span v-if="selectedName" class="file-name">{{ selectedName }}</span>
    <span v-if="hintText" class="hint-text">{{ hintText }}</span>
  </div>
</template>

<script>
export default {
  name: 'LocalImagePicker',
  props: {
    accept: {
      type: String,
      default: 'image/*'
    },
    buttonText: {
      type: String,
      default: '选择图片'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    hintText: {
      type: String,
      default: ''
    },
    selectedName: {
      type: String,
      default: ''
    }
  },
  methods: {
    triggerPick() {
      if (this.disabled || !this.$refs.fileInput) return
      this.$refs.fileInput.click()
    },
    onPickFile(event) {
      const file = event && event.target && event.target.files && event.target.files[0]
      if (file) this.$emit('pick', file)
      if (event && event.target) event.target.value = ''
    }
  }
}
</script>

<style lang="scss" scoped>
.picker {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.picker-input {
  display: none;
}

.ghost-btn {
  padding: 8px 14px;
  font-size: 13px;
  @include ghost-button($height: 38px, $radius: 18px, $font-size: 13px);
}

.file-name {
  color: #4e584f;
  font-size: 12px;
  word-break: break-all;
}

.hint-text {
  color: $color-muted-soft;
  font-size: 12px;
}
</style>
