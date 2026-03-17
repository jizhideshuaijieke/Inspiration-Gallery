<template>
  <section class="create-page">
    <PagePanel class="create-panel" title="创作">
      <div class="studio-shell">
        <div class="previews-row">
          <section class="stage-card">
            <div class="section-bar">
              <p class="field-label">原图</p>
              <LocalImagePicker
                button-text="选择图片"
                :selected-name="selectedFileName"
                hint-text="选好图片后即可开始生成"
                @pick="onPickFile"
              />
            </div>

            <div class="preview-frame">
              <img v-if="previewUrl" :src="previewUrl" alt="input preview" class="preview-image" />
              <EmptyState v-else title="还没有图片" description="选择一张图片开始创作。" />
            </div>
          </section>

          <section class="stage-card">
            <div class="section-bar">
              <p class="field-label">生成预览</p>
              <span class="status-pill" :class="`is-${taskStatus}`">{{ taskStatusLabel }}</span>
            </div>

            <div class="preview-frame">
              <img
                v-if="generatedPreviewUrl && !generatedPreviewLoadFailed"
                :src="generatedPreviewUrl"
                alt="generated preview"
                class="preview-image"
                @error="onGeneratedPreviewError"
              />
              <EmptyState v-else :title="outputPreviewTitle" :description="outputPreviewDescription" />
            </div>
          </section>
        </div>

        <div class="workspace-row">
          <section class="workspace-card style-panel">
            <div class="section-bar compact">
              <p class="field-label">风格选择</p>
            </div>

            <div class="style-list">
              <button
                v-for="style in styles"
                :key="style.id"
                type="button"
                class="style-item"
                :class="{ active: selectedStyleId === style.id }"
                @click="selectedStyleId = style.id"
              >
                <span class="style-name">{{ style.name }}</span>
                <span class="style-code">{{ style.code }}</span>
              </button>
            </div>
          </section>

          <section class="workspace-card control-panel">
            <div class="section-bar compact">
              <p class="field-label">设置</p>
              <span class="task-chip">任务 {{ taskIdText }}</span>
            </div>

            <div class="mini-summary">
              <article class="mini-card">
                <span class="mini-label">已选风格</span>
                <strong class="mini-value">{{ selectedStyleName }}</strong>
              </article>
              <article class="mini-card">
                <span class="mini-label">当前状态</span>
                <strong class="mini-value">{{ taskStatusLabel }}</strong>
              </article>
            </div>

            <label class="field-label control-label" for="artwork-title">作品标题</label>
            <input
              id="artwork-title"
              v-model.trim="title"
              type="text"
              maxlength="100"
              class="text-input"
              placeholder="给作品起个名字"
            />

            <label class="toggle-line">
              <input v-model="publishToHall" type="checkbox" />
              <span>保存后发布到大厅</span>
            </label>

            <p
              v-if="feedbackText"
              class="feedback-text"
              :class="feedbackToneClass"
            >
              {{ feedbackText }}
            </p>

            <div class="action-row">
              <button
                type="button"
                class="primary-btn"
                :disabled="creatingTask || !canCreateTask"
                @click="createTask"
              >
                {{ creatingTask ? '生成中...' : '开始生成' }}
              </button>

              <button
                type="button"
                class="ghost-btn"
                :disabled="pollingTask || !taskId"
                @click="manualRefreshTask"
              >
                查看状态
              </button>

              <button
                type="button"
                class="primary-btn secondary-btn"
                :disabled="!canSaveArtwork || savingArtwork"
                @click="saveArtwork"
              >
                {{ savingArtwork ? '保存中...' : '保存作品' }}
              </button>
            </div>
          </section>
        </div>
      </div>
    </PagePanel>
  </section>
</template>

<script>
import PagePanel from '../components/common/PagePanel.vue'
import EmptyState from '../components/common/EmptyState.vue'
import LocalImagePicker from '../components/common/LocalImagePicker.vue'
import { getStyles } from '../api/styles'
import { createStyleTransferTask, getTask, uploadTaskInputImage } from '../api/tasks'
import { createArtwork, getArtworkDetail, updateArtwork } from '../api/artworks'
import { createTaskSocket } from '../utils/taskSocket'

const TASK_STATUS_LABEL = {
  idle: '未开始',
  pending: '生成中',
  running: '生成中',
  success: '已完成',
  failed: '失败'
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function isTerminalTaskStatus(status) {
  return status === 'success' || status === 'failed'
}

function getErrorMessage(error, fallback) {
  return (
    (error &&
      error.response &&
      error.response.data &&
      error.response.data.message) ||
    fallback
  )
}

export default {
  name: 'CreateView',
  components: {
    PagePanel,
    EmptyState,
    LocalImagePicker
  },
  data() {
    return {
      styles: [],
      selectedStyleId: null,
      title: '',
      publishToHall: false,
      selectedFile: null,
      previewUrl: '',
      creatingTask: false,
      pollingTask: false,
      savingArtwork: false,
      taskId: null,
      taskStatus: 'idle',
      createdArtworkId: null,
      generatedPreviewUrl: '',
      generatedPreviewLoadFailed: false,
      errorMsg: '',
      message: '',
      taskWarning: '',
      pollingStopped: false,
      taskSocket: null,
      taskSocketTaskId: null,
      taskSocketCloseMuted: false
    }
  },
  computed: {
    canCreateTask() {
      return Boolean(this.selectedFile && this.selectedStyleId)
    },
    canSaveArtwork() {
      return this.taskStatus === 'success' && !this.createdArtworkId
    },
    selectedFileName() {
      return this.selectedFile ? this.selectedFile.name : ''
    },
    selectedStyleName() {
      const selected = this.styles.find((item) => item.id === this.selectedStyleId)
      return selected ? selected.name : '未选'
    },
    taskIdText() {
      return this.taskId ? `#${this.taskId}` : '未开始'
    },
    taskStatusLabel() {
      return TASK_STATUS_LABEL[this.taskStatus] || this.taskStatus
    },
    outputPreviewTitle() {
      if (this.generatedPreviewLoadFailed) return '预览加载失败'
      if (!this.taskId) return '等待生成'
      if (this.taskStatus === 'pending' || this.taskStatus === 'running') return '正在生成'
      if (this.taskStatus === 'failed') return '生成失败'
      if (this.taskStatus === 'success') return '图片加载中'
      return '暂无预览'
    },
    outputPreviewDescription() {
      if (this.generatedPreviewLoadFailed) return '预览暂时打不开，请稍后再试。'
      if (!this.taskId) return '生成结果会显示在这里。'
      if (this.taskStatus === 'pending' || this.taskStatus === 'running') return '请稍等片刻。'
      if (this.taskStatus === 'failed') return '换一张图片或风格再试试。'
      if (this.taskStatus === 'success') return '可以直接保存作品。'
      return ''
    },
    feedbackText() {
      return this.errorMsg || this.taskWarning || this.message || ''
    },
    feedbackToneClass() {
      if (this.errorMsg) return 'is-error'
      if (this.taskWarning) return 'is-warn'
      return 'is-ok'
    }
  },
  methods: {
    onPickFile(file) {
      if (!file) return
      if (this.previewUrl) URL.revokeObjectURL(this.previewUrl)
      this.selectedFile = file
      this.previewUrl = URL.createObjectURL(file)
      this.resetTaskState()
      this.errorMsg = ''
      this.message = ''
      this.taskWarning = ''
    },
    onGeneratedPreviewError() {
      this.generatedPreviewLoadFailed = true
    },
    async reloadStyles() {
      this.errorMsg = ''
      try {
        const res = await getStyles()
        const list = (res && res.data && res.data.data && res.data.data.list) || []
        this.styles = list
        if (!this.selectedStyleId && list.length) this.selectedStyleId = list[0].id
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '风格加载失败')
      }
    },
    resetTaskState() {
      this.disconnectTaskSocket()
      this.taskId = null
      this.taskStatus = 'idle'
      this.createdArtworkId = null
      this.generatedPreviewUrl = ''
      this.generatedPreviewLoadFailed = false
      this.pollingStopped = false
      this.taskWarning = ''
    },
    async createTask() {
      if (!this.canCreateTask || this.creatingTask) return
      this.creatingTask = true
      this.errorMsg = ''
      this.message = ''
      this.taskWarning = ''
      this.resetTaskState()

      try {
        const uploadRes = await uploadTaskInputImage(this.selectedFile)
        const uploadData = (uploadRes && uploadRes.data && uploadRes.data.data) || {}
        if (!uploadData.input_image_url) {
          throw new Error('上传图片失败')
        }

        const res = await createStyleTransferTask({
          style_id: this.selectedStyleId,
          input_image_url: uploadData.input_image_url
        })
        const data = (res && res.data && res.data.data) || {}
        this.taskId = data.task_id || null
        this.taskStatus = data.status || 'pending'
        if (data.preview_url) {
          this.generatedPreviewUrl = data.preview_url
          this.generatedPreviewLoadFailed = false
        }
        this.message = `已创建任务（#${this.taskId}）`
        if (this.taskId) this.startTaskTracking()
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '创建任务失败')
      } finally {
        this.creatingTask = false
      }
    },
    startTaskTracking() {
      this.taskWarning = ''
      if (!this.openTaskSocket()) {
        this.startPollingTask()
      }
    },
    openTaskSocket() {
      if (!this.taskId || typeof WebSocket === 'undefined') return false
      if (this.taskSocket && this.taskSocketTaskId === this.taskId) return true

      this.disconnectTaskSocket()

      const socket = createTaskSocket(this.taskId, {
        token: localStorage.getItem('token'),
        onMessage: this.handleTaskSocketMessage,
        onClose: this.handleTaskSocketClose,
        onError: this.handleTaskSocketError
      })

      if (!socket) return false

      this.taskSocket = socket
      this.taskSocketTaskId = this.taskId
      this.taskSocketCloseMuted = false
      return true
    },
    disconnectTaskSocket() {
      if (!this.taskSocket) {
        this.taskSocketTaskId = null
        this.taskSocketCloseMuted = false
        return
      }

      const socket = this.taskSocket
      this.taskSocketCloseMuted = true
      this.taskSocket = null
      this.taskSocketTaskId = null
      socket.close()
    },
    handleTaskSocketMessage(data) {
      this.taskWarning = ''
      this.applyTaskPayload(data)
    },
    handleTaskSocketError() {
      // Let the close callback fall back to polling.
    },
    handleTaskSocketClose() {
      const muted = this.taskSocketCloseMuted
      const shouldFallback = Boolean(this.taskId) && !isTerminalTaskStatus(this.taskStatus)

      this.taskSocket = null
      this.taskSocketTaskId = null
      this.taskSocketCloseMuted = false

      if (!muted && shouldFallback && !this.pollingTask) {
        this.startPollingTask()
      }
    },
    applyTaskPayload(data) {
      this.taskStatus = data.status || 'pending'

      if (data.preview_url) {
        this.generatedPreviewUrl = data.preview_url
        this.generatedPreviewLoadFailed = false
      }

      if (data.output_artwork_id) {
        const needsHydration = !data.preview_url && data.output_artwork_id !== this.createdArtworkId
        this.createdArtworkId = data.output_artwork_id
        if (needsHydration) {
          this.hydratePreviewFromArtwork(data.output_artwork_id)
        }
      }

      if (data.status === 'failed' && data.error_msg) {
        this.errorMsg = data.error_msg
      }

      if (isTerminalTaskStatus(data.status)) {
        this.disconnectTaskSocket()
      }
    },
    async startPollingTask() {
      if (!this.taskId || this.pollingTask) return
      this.pollingTask = true
      this.pollingStopped = false

      try {
        for (let i = 0; i < 45; i += 1) {
          if (this.pollingStopped) break
          await this.fetchTaskStatus()
          if (this.taskStatus === 'success' || this.taskStatus === 'failed') break
          await wait(2000)
        }

        if (this.taskStatus !== 'success' && this.taskStatus !== 'failed') {
          this.taskWarning = '任务还在处理中，可以稍后再刷新。'
        }
      } finally {
        this.pollingTask = false
      }
    },
    async hydratePreviewFromArtwork(artworkId) {
      if (!artworkId) return
      try {
        const res = await getArtworkDetail(artworkId)
        const data = (res && res.data && res.data.data) || {}
        if (data.result_image_url) {
          this.generatedPreviewUrl = data.result_image_url
          this.generatedPreviewLoadFailed = false
        }
      } catch (_) {
        // Preview fallback is already handled by the status copy.
      }
    },
    async fetchTaskStatus() {
      if (!this.taskId) return
      const res = await getTask(this.taskId)
      const data = (res && res.data && res.data.data) || {}
      this.applyTaskPayload(data)
    },
    async manualRefreshTask() {
      this.errorMsg = ''
      try {
        await this.fetchTaskStatus()
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '刷新任务状态失败')
      }
    },
    async saveArtwork() {
      if (!this.canSaveArtwork || this.savingArtwork) return
      this.savingArtwork = true
      this.errorMsg = ''

      try {
        const saveRes = await createArtwork({
          task_id: this.taskId,
          title: this.title || '未命名作品'
        })
        const saveData = (saveRes && saveRes.data && saveRes.data.data) || {}
        const artworkId = saveData.artwork_id
        this.createdArtworkId = artworkId
        await this.hydratePreviewFromArtwork(artworkId)

        if (this.publishToHall && artworkId) {
          await updateArtwork(artworkId, { visibility: 'hall' })
          this.message = `作品已发布到大厅（ID: ${artworkId}）`
        } else {
          this.message = `作品已保存到仓库（ID: ${artworkId}）`
        }
      } catch (error) {
        this.errorMsg = getErrorMessage(error, '保存作品失败')
      } finally {
        this.savingArtwork = false
      }
    }
  },
  mounted() {
    this.reloadStyles()
  },
  activated() {
    if (this.taskId && !isTerminalTaskStatus(this.taskStatus)) {
      this.pollingStopped = false
      this.startTaskTracking()
    }
  },
  deactivated() {
    this.pollingStopped = true
    this.disconnectTaskSocket()
  },
  beforeDestroy() {
    this.pollingStopped = true
    this.disconnectTaskSocket()
    if (this.previewUrl) URL.revokeObjectURL(this.previewUrl)
  }
}
</script>

<style lang="scss" scoped>
.create-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

:deep(.create-panel) {
  height: 100%;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}

:deep(.create-panel .panel-header) {
  padding-bottom: 12px;
}

:deep(.create-panel .panel-body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding-top: 12px;
}

.studio-shell {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 14px;
}

.previews-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.workspace-row {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
  gap: 14px;
}

.stage-card,
.workspace-card {
  @include panel-surface(
    $radius: $radius-lg,
    $border: #e2e8de,
    $background: linear-gradient(180deg, #ffffff 0%, #fbfcfa 100%),
    $shadow: none
  );
  padding: 14px;
}

.workspace-card {
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.section-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-bar.compact {
  margin-bottom: 14px;
}

.field-label {
  margin: 0;
  font-size: 13px;
  color: $color-text-soft;
  font-weight: 700;
}

.preview-frame {
  height: clamp(280px, 35vh, 360px);
  border: 1px solid #dfe5db;
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(244, 247, 241, 0.92), rgba(248, 250, 246, 0.96)),
    radial-gradient(circle at top, rgba(221, 234, 221, 0.65), transparent 58%);
  overflow: hidden;
  display: flex;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background: #f1f3ef;
}

:deep(.preview-frame .empty-state) {
  width: 100%;
  border: 0;
  border-radius: 0;
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.style-panel {
  min-height: 0;
}

.style-list {
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  align-content: start;
}

.style-item {
  border: 1px solid #d7ddd4;
  border-radius: $radius-md;
  background: $color-surface;
  text-align: left;
  padding: 11px 14px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  transition:
    border-color $transition-fast,
    background $transition-fast,
    transform $transition-fast;

  &:hover {
    transform: translateY(-1px);
    border-color: #b7d0b6;
  }

  &.active {
    border-color: $color-primary-soft;
    background: #eef8ef;
  }
}

.style-name {
  color: #1f2a22;
  font-size: 16px;
  font-weight: 700;
}

.style-code {
  font-size: 11px;
  color: #6f786e;
}

.control-panel {
  justify-content: flex-start;
}

.task-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f2f5ef;
  color: #556056;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.mini-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.mini-card {
  border: 1px solid #e3e8df;
  border-radius: 14px;
  background: #f8faf7;
  padding: 10px 12px;
}

.mini-label {
  display: block;
  color: #7a8479;
  font-size: 11px;
}

.mini-value {
  display: block;
  margin-top: 5px;
  color: #223026;
  font-size: 16px;
}

.control-label {
  margin-bottom: 8px;
}

.text-input {
  @include input-shell($height: 42px, $radius: $radius-md, $padding-x: 12px);
}

.toggle-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0 0;
  font-size: 13px;
  color: #495249;
}

.status-pill {
  padding: 7px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: #eef1ec;
  color: #556056;
  white-space: nowrap;

  &.is-success {
    background: $color-success-bg;
    color: $color-success-text;
  }

  &.is-failed {
    background: $color-error-bg;
    color: #ba3b5b;
  }

  &.is-pending,
  &.is-running {
    background: $color-warn-bg;
    color: $color-warn-text;
  }
}

.feedback-text {
  margin: 10px 0 0;
  font-size: 13px;
  line-height: 1.5;

  &.is-warn {
    color: #8b6a28;
  }

  &.is-ok {
    color: $color-primary;
  }

  &.is-error {
    color: $color-error-text;
  }
}

.action-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.primary-btn,
.ghost-btn {
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
}

.primary-btn {
  @include solid-button($height: 40px, $radius: $radius-md, $font-size: 12px);

  &[disabled] {
    background: #95a497;
  }
}

.secondary-btn {
  background: #3f7d4f;
}

.ghost-btn {
  @include ghost-button($height: 40px, $radius: $radius-md, $font-size: 12px);
}

@media (max-width: 1180px) {
  .workspace-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 980px) {
  .create-page {
    height: auto;
    overflow: auto;
  }

  :deep(.create-panel) {
    height: auto;
  }

  .studio-shell {
    display: block;
  }

  .previews-row,
  .workspace-row {
    display: grid;
    grid-template-columns: 1fr;
    margin-bottom: 14px;
  }

  .preview-frame {
    height: 340px;
  }
}

@media (max-width: 640px) {
  .style-list,
  .mini-summary,
  .action-row {
    grid-template-columns: 1fr;
  }

  .section-bar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
