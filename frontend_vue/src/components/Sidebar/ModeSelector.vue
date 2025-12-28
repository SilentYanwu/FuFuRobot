<template>
  <div class="nav-group">
    <h3 class="text-xs uppercase tracking-wider text-gray-400 mb-4 font-semibold">功能模式</h3>

    <label
      v-for="mode in chatModes"
      :key="mode.id"
      class="nav-item"
      :class="{ active: mode.id === currentMode }"
    >
      <input
        type="radio"
        name="mode"
        :value="mode.id"
        v-model="selectedMode"
        @change="handleModeChange(mode.id)"
      />
      <span>{{ mode.icon }} {{ mode.name }}</span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/counter'

const chatStore = useChatStore()
const { chatModes } = chatStore
const { currentMode } = storeToRefs(chatStore)

const selectedMode = ref(currentMode)

const emit = defineEmits<{
  modeChange: [mode: 'chat' | 'focus' | 'text2sql']
}>()

const handleModeChange = (mode: 'chat' | 'focus' | 'text2sql') => {
  emit('modeChange', mode)
}

// 监听外部模式变化
watch(currentMode, (newMode: 'chat' | 'focus' | 'text2sql') => {
  selectedMode.value = newMode
})
</script>

<style scoped></style>
