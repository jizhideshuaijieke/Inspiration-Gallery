<template>
  <div v-if="visible" class="mask" @click.self="$emit('close')">
    <div class="modal">
      <button type="button" class="close-btn" @click="$emit('close')">x</button>
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.mask {
  position: fixed;
  inset: 0;
  z-index: 120;
  background: rgba(30, 33, 31, 0.42);
  display: grid;
  place-items: center;
  padding: 18px;
}

.modal {
  position: relative;
  width: min(1160px, 96vw);
  max-height: 90vh;
  border-radius: 22px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 28px 80px rgba(27, 34, 29, 0.16);
}

.close-btn {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 2;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 999px;
  background: rgba(31, 36, 33, 0.42);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
}
</style>
