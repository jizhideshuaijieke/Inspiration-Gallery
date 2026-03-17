<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  --ink: #1f2421;
  --muted: #7b837b;
  --edge: #e4e6e1;
  --accent: #ff335f;
}

html,
body,
#app {
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  background: #f4f4f0;
  color: var(--ink);
  font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

button,
input,
textarea {
  font: inherit;
}

@media (max-width: 980px) {
  body {
    overflow: auto;
  }
}
</style>
