<template>
  <div class="loading-dots">
    <span></span>
    <span></span>
    <span></span>
  </div>
</template>

<script setup lang="ts">
// 无需逻辑，仅用于展示加载动画
</script>

<style scoped>
.loading-dots span {
  animation-delay: calc(var(--i) * 0.16s);
}

.loading-dots span:nth-child(1) {
  --i: 0;
}

.loading-dots span:nth-child(2) {
  --i: 1;
}

.loading-dots span:nth-child(3) {
  --i: 2;
}
</style>
