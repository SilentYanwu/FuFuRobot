<template>
  <div
    class="message-avatar"
    :class="[
      role,
      role === 'user'
        ? 'bg-linear-to-r from-indigo-500 to-purple-600 text-white mr-0 ml-3'
        : 'bg-linear-to-r from-blue-500 to-slate-700 text-white',
    ]"
  >
    <img v-if="!imageError" :src="avatarSrc" :alt="role" @error="handleImageError" />
    <span v-else class="fallback-icon text-2xl">{{ role === 'user' ? '👤' : '🤖' }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  role: 'user' | 'ai'
}

const props = defineProps<Props>()

const imageError = ref(false)

const avatarSrc = computed(() => {
  if (props.role === 'user') {
    return '/src/assets/images/user.png'
  } else {
    return '/src/assets/images/robot.png'
  }
})

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
/* 所有样式已移至模板中的class属性 */
</style>
