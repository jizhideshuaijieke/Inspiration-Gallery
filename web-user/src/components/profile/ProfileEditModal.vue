<template>
  <div v-if="visible" class="profile-mask" @click.self="handleClose">
    <div class="profile-modal">
      <button type="button" class="close-btn" @click="handleClose">x</button>

      <section class="crop-panel">
        <header class="panel-head">
          <h3 class="panel-title">修改资料</h3>
          <p class="panel-subtitle">上传图片后可拖动和缩放，保存为新头像。</p>
        </header>

        <div
          ref="cropViewport"
          class="crop-viewport"
          :class="{ 'is-draggable': Boolean(localPreviewUrl), 'is-dragging': dragging }"
          @pointerdown="onPointerDown"
        >
          <img
            v-if="localPreviewUrl"
            ref="cropImage"
            class="crop-image"
            :src="localPreviewUrl"
            :style="cropImageStyle"
            alt="avatar crop"
            draggable="false"
            @load="onCropImageLoad"
          />
          <img
            v-else-if="currentAvatarUrl"
            class="fallback-avatar"
            :src="currentAvatarUrl"
            alt="current avatar"
          />
          <span v-else class="fallback-initial">{{ profileInitial }}</span>

          <div class="crop-shadow" />
          <div class="crop-ring" />
        </div>

        <div class="crop-controls">
          <label class="slider-line">
            <span>缩放</span>
            <input
              v-model.number="zoom"
              type="range"
              min="1"
              max="4"
              step="0.01"
              :disabled="!localPreviewUrl"
              @input="onZoomChange"
            />
          </label>

          <button
            type="button"
            class="ghost-btn"
            :disabled="!localPreviewUrl"
            @click="resetCropPosition"
          >
            重置裁剪
          </button>
        </div>

        <LocalImagePicker
          button-text="从本地上传头像"
          :selected-name="selectedFileName"
          hint-text="支持 jpg / png / webp / bmp"
          @pick="onPickAvatar"
        />
      </section>

      <section class="form-panel">
        <div class="preview-card">
          <div class="preview-avatar">
            <img
              v-if="localPreviewUrl"
              class="preview-crop-image"
              :src="localPreviewUrl"
              :style="summaryImageStyle"
              alt="avatar preview"
            />
            <img
              v-else-if="currentAvatarUrl"
              class="preview-static-image"
              :src="currentAvatarUrl"
              alt="avatar preview"
            />
            <span v-else>{{ profileInitial }}</span>
          </div>
          <p class="preview-name">{{ previewUsername }}</p>
          <p class="preview-tip">保存后会同步更新头像。</p>
        </div>

        <label class="field-label">用户名</label>
        <input
          v-model.trim="draft.username"
          type="text"
          maxlength="32"
          class="text-input"
          placeholder="请输入用户名"
          @input="clearLocalError"
        />
        <p class="field-hint">用户名可使用字母、数字和下划线。</p>

        <p v-if="localError" class="error-text">{{ localError }}</p>
        <p v-if="submitError" class="error-text">{{ submitError }}</p>

        <div class="action-row">
          <button type="button" class="primary-btn" :disabled="saving" @click="onSubmit">
            {{ saving ? '保存中...' : '保存资料' }}
          </button>
          <button type="button" class="ghost-btn" :disabled="saving" @click="handleClose">
            取消
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import LocalImagePicker from '../common/LocalImagePicker.vue'

const USERNAME_PATTERN = /^[a-zA-Z0-9_]+$/
const FALLBACK_VIEWPORT_SIZE = 320
const SUMMARY_SIZE = 112

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

export default {
  name: 'ProfileEditModal',
  components: {
    LocalImagePicker
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    profile: {
      type: Object,
      default: null
    },
    saving: {
      type: Boolean,
      default: false
    },
    submitError: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      draft: {
        username: ''
      },
      localError: '',
      currentAvatarUrl: '',
      selectedFile: null,
      selectedFileName: '',
      localPreviewUrl: '',
      cropViewportSize: FALLBACK_VIEWPORT_SIZE,
      imageNaturalWidth: 0,
      imageNaturalHeight: 0,
      zoom: 1,
      offsetX: 0,
      offsetY: 0,
      dragging: false,
      dragPointerId: null,
      dragStartX: 0,
      dragStartY: 0,
      dragOriginX: 0,
      dragOriginY: 0
    }
  },
  computed: {
    profileInitial() {
      const source = (this.draft.username || (this.profile && this.profile.username) || '').trim()
      return source ? source[0].toUpperCase() : '?'
    },
    previewUsername() {
      const value = (this.draft.username || '').trim()
      return value || '未设置用户名'
    },
    baseScale() {
      if (!this.imageNaturalWidth || !this.imageNaturalHeight) return 1
      return Math.max(
        this.cropViewportSize / this.imageNaturalWidth,
        this.cropViewportSize / this.imageNaturalHeight
      )
    },
    displayScale() {
      return this.baseScale * this.zoom
    },
    cropImageStyle() {
      return this.buildImageStyle(this.cropViewportSize)
    },
    summaryImageStyle() {
      return this.buildImageStyle(SUMMARY_SIZE)
    }
  },
  watch: {
    visible(next) {
      if (next) {
        this.resetDraft()
      } else {
        this.stopDragging()
      }
    },
    profile: {
      deep: true,
      handler() {
        if (this.visible) this.resetDraft()
      }
    }
  },
  mounted() {
    window.addEventListener('pointermove', this.onPointerMove)
    window.addEventListener('pointerup', this.stopDragging)
    window.addEventListener('pointercancel', this.stopDragging)
    window.addEventListener('resize', this.onResize)
  },
  beforeDestroy() {
    this.stopDragging()
    this.revokeLocalPreview()
    window.removeEventListener('pointermove', this.onPointerMove)
    window.removeEventListener('pointerup', this.stopDragging)
    window.removeEventListener('pointercancel', this.stopDragging)
    window.removeEventListener('resize', this.onResize)
  },
  methods: {
    handleClose() {
      if (this.saving) return
      this.$emit('close')
    },
    resetDraft() {
      this.revokeLocalPreview()
      this.stopDragging()
      this.draft = {
        username: (this.profile && this.profile.username) || ''
      }
      this.localError = ''
      this.currentAvatarUrl = (this.profile && this.profile.avatar_url) || ''
      this.selectedFile = null
      this.selectedFileName = ''
      this.localPreviewUrl = ''
      this.imageNaturalWidth = 0
      this.imageNaturalHeight = 0
      this.zoom = 1
      this.offsetX = 0
      this.offsetY = 0
      this.$nextTick(() => {
        this.measureViewport()
      })
    },
    revokeLocalPreview() {
      if (this.localPreviewUrl) {
        URL.revokeObjectURL(this.localPreviewUrl)
      }
      this.localPreviewUrl = ''
    },
    measureViewport() {
      const nextSize =
        (this.$refs.cropViewport && this.$refs.cropViewport.clientWidth) || FALLBACK_VIEWPORT_SIZE
      if (!nextSize) return

      const previousSize = this.cropViewportSize || nextSize
      const ratio = nextSize / previousSize
      this.cropViewportSize = nextSize

      if (ratio !== 1) {
        this.offsetX *= ratio
        this.offsetY *= ratio
        this.clampOffsets()
      }
    },
    onResize() {
      if (!this.visible) return
      this.measureViewport()
    },
    clearLocalError() {
      this.localError = ''
    },
    onPickAvatar(file) {
      if (!file) return
      if (file.type && !file.type.startsWith('image/')) {
        this.localError = '请选择图片'
        return
      }

      this.revokeLocalPreview()
      this.clearLocalError()
      this.selectedFile = file
      this.selectedFileName = file.name || '已选择图片'
      this.localPreviewUrl = URL.createObjectURL(file)
      this.imageNaturalWidth = 0
      this.imageNaturalHeight = 0
      this.zoom = 1
      this.offsetX = 0
      this.offsetY = 0
      this.$nextTick(() => {
        this.measureViewport()
      })
    },
    onCropImageLoad(event) {
      const image = event && event.target
      if (!image) return
      this.measureViewport()
      this.imageNaturalWidth = image.naturalWidth || 0
      this.imageNaturalHeight = image.naturalHeight || 0
      this.resetCropPosition()
    },
    onZoomChange() {
      this.clampOffsets()
    },
    resetCropPosition() {
      this.zoom = 1
      this.offsetX = 0
      this.offsetY = 0
      this.clampOffsets()
    },
    clampOffsets() {
      if (!this.imageNaturalWidth || !this.imageNaturalHeight) return

      const scaledWidth = this.imageNaturalWidth * this.displayScale
      const scaledHeight = this.imageNaturalHeight * this.displayScale
      const maxOffsetX = Math.max((scaledWidth - this.cropViewportSize) / 2, 0)
      const maxOffsetY = Math.max((scaledHeight - this.cropViewportSize) / 2, 0)

      this.offsetX = clamp(this.offsetX, -maxOffsetX, maxOffsetX)
      this.offsetY = clamp(this.offsetY, -maxOffsetY, maxOffsetY)
    },
    buildImageStyle(targetSize) {
      if (!this.localPreviewUrl || !this.cropViewportSize) return {}
      const ratio = targetSize / this.cropViewportSize
      const translateX = this.offsetX * ratio
      const translateY = this.offsetY * ratio

      return {
        transform: `translate(calc(-50% + ${translateX}px), calc(-50% + ${translateY}px)) scale(${this.displayScale * ratio})`
      }
    },
    onPointerDown(event) {
      if (!this.localPreviewUrl || !event.isPrimary) return
      event.preventDefault()
      this.dragging = true
      this.dragPointerId = event.pointerId
      this.dragStartX = event.clientX
      this.dragStartY = event.clientY
      this.dragOriginX = this.offsetX
      this.dragOriginY = this.offsetY
    },
    onPointerMove(event) {
      if (!this.dragging || event.pointerId !== this.dragPointerId) return
      event.preventDefault()
      this.offsetX = this.dragOriginX + (event.clientX - this.dragStartX)
      this.offsetY = this.dragOriginY + (event.clientY - this.dragStartY)
      this.clampOffsets()
    },
    stopDragging(event) {
      if (event && this.dragPointerId !== null && event.pointerId !== this.dragPointerId) return
      this.dragging = false
      this.dragPointerId = null
    },
    validateDraft() {
      const username = (this.draft.username || '').trim()
      if (!username) return '请输入用户名'
      if (username.length < 3 || username.length > 32) return '用户名长度为 3-32 位'
      if (!USERNAME_PATTERN.test(username)) return '用户名只能包含字母、数字和下划线'
      return ''
    },
    buildAvatarFile() {
      if (!this.localPreviewUrl) return Promise.resolve(null)

      const image = this.$refs.cropImage
      if (!image || !this.imageNaturalWidth || !this.imageNaturalHeight) {
        return Promise.reject(new Error('头像还没加载好，请稍后再试'))
      }

      const sourceSize = this.cropViewportSize / this.displayScale
      const centerX = this.imageNaturalWidth / 2 - this.offsetX / this.displayScale
      const centerY = this.imageNaturalHeight / 2 - this.offsetY / this.displayScale
      const maxSourceX = Math.max(this.imageNaturalWidth - sourceSize, 0)
      const maxSourceY = Math.max(this.imageNaturalHeight - sourceSize, 0)
      const sourceX = clamp(centerX - sourceSize / 2, 0, maxSourceX)
      const sourceY = clamp(centerY - sourceSize / 2, 0, maxSourceY)

      const canvas = document.createElement('canvas')
      canvas.width = 512
      canvas.height = 512

      const context = canvas.getContext('2d')
      if (!context) {
        return Promise.reject(new Error('当前浏览器不支持裁剪头像'))
      }

      context.drawImage(image, sourceX, sourceY, sourceSize, sourceSize, 0, 0, 512, 512)

      return new Promise((resolve, reject) => {
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('头像裁剪失败'))
              return
            }

            resolve(new File([blob], `avatar-${Date.now()}.png`, { type: 'image/png' }))
          },
          'image/png',
          0.92
        )
      })
    },
    async onSubmit() {
      const validationMessage = this.validateDraft()
      if (validationMessage) {
        this.localError = validationMessage
        return
      }

      this.localError = ''

      try {
        const avatarFile = await this.buildAvatarFile()
        this.$emit('submit', {
          username: this.draft.username.trim(),
          avatarFile
        })
      } catch (error) {
        this.localError = (error && error.message) || '头像裁剪失败'
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.profile-mask {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(27, 34, 29, 0.44);
  display: grid;
  place-items: center;
  padding: 18px;
}

.profile-modal {
  width: min(1080px, 96vw);
  min-height: min(82vh, 760px);
  background: #fff;
  border-radius: 22px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  overflow: hidden;
  position: relative;
  box-shadow: $shadow-large;
}

.close-btn {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 3;
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 50%;
  background: rgba(23, 28, 25, 0.45);
  color: #fff;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
}

.crop-panel {
  background:
    radial-gradient(circle at top, rgba(209, 229, 210, 0.92), transparent 52%),
    linear-gradient(180deg, #f4f8f1 0%, #eef3eb 100%);
  padding: 34px 28px 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel-head {
  padding-right: 42px;
}

.panel-title {
  margin: 0;
  font-size: 24px;
  color: $color-text;
}

.panel-subtitle {
  margin: 8px 0 0;
  font-size: 13px;
  color: $color-muted;
}

.crop-viewport {
  width: min(100%, 360px);
  aspect-ratio: 1 / 1;
  border-radius: 28px;
  background: linear-gradient(145deg, #dce6d6, #f7faf4);
  position: relative;
  overflow: hidden;
  align-self: center;
  touch-action: none;
}

.crop-viewport.is-draggable {
  cursor: grab;
}

.crop-viewport.is-dragging {
  cursor: grabbing;
}

.crop-image,
.preview-crop-image {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center center;
  user-select: none;
  pointer-events: none;
}

.fallback-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.fallback-initial {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #304137;
  font-size: 88px;
  font-weight: 700;
}

.crop-shadow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle, transparent 0 38%, rgba(26, 36, 30, 0.16) 38%, rgba(26, 36, 30, 0.32) 100%);
  pointer-events: none;
}

.crop-ring {
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.92);
  box-shadow: 0 0 0 999px rgba(23, 30, 26, 0.06);
  pointer-events: none;
}

.crop-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.slider-line {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #314137;
  font-size: 13px;
}

.slider-line input {
  width: 180px;
}

.form-panel {
  border-left: 1px solid #e7ece3;
  padding: 34px 24px 28px;
  display: flex;
  flex-direction: column;
}

.preview-card {
  border: 1px solid #e0e7db;
  border-radius: 20px;
  background: linear-gradient(180deg, #fbfcfa 0%, #f4f6f2 100%);
  padding: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 18px;
}

.preview-avatar {
  width: 112px;
  height: 112px;
  border-radius: 50%;
  background: #eef2ea;
  color: #334239;
  display: grid;
  place-items: center;
  position: relative;
  overflow: hidden;
  font-size: 42px;
  font-weight: 700;
}

.preview-static-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-name {
  margin: 14px 0 4px;
  color: #203026;
  font-size: 20px;
  font-weight: 700;
}

.preview-tip {
  margin: 0;
  color: #728073;
  font-size: 12px;
}

.field-label {
  display: block;
  margin: 0 0 8px;
  color: $color-text-soft;
  font-size: 13px;
}

.text-input {
  @include input-shell($height: 44px, $radius: $radius-md, $padding-x: 14px);
}

.field-hint {
  margin: 8px 0 0;
  color: #748073;
  font-size: 12px;
}

.action-row {
  margin-top: auto;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.primary-btn {
  padding: 10px 16px;
  font-size: 13px;
  @include solid-button($height: 40px, $radius: 18px, $font-size: 13px);
}

.ghost-btn {
  padding: 10px 16px;
  font-size: 13px;
  @include ghost-button($height: 40px, $radius: 18px, $font-size: 13px);
}

.error-text {
  margin: 12px 0 0;
  color: $color-error-text;
  font-size: 13px;
}

@media (max-width: 980px) {
  .profile-modal {
    grid-template-columns: 1fr;
    max-height: 92vh;
    overflow: auto;
  }

  .form-panel {
    border-left: 0;
    border-top: 1px solid #e7ece3;
  }

  .action-row {
    margin-top: 18px;
  }
}

@media (max-width: 640px) {
  .crop-panel,
  .form-panel {
    padding: 28px 16px 20px;
  }

  .crop-viewport {
    width: min(100%, 300px);
  }

  .slider-line {
    width: 100%;
    justify-content: space-between;
  }

  .slider-line input {
    width: 150px;
  }
}
</style>
