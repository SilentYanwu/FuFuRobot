<template>
  <aside class="sidebar">
    <div
      class="text-2xl font-bold mb-10 text-center text-blue-400 flex items-center justify-center gap-2.5 pb-5 border-b-2 border-white/10"
    >
      君 の fufu
    </div>

    <ModeSelector @mode-change="handleModeChange" />

    <div class="tips">
      <h4 class="text-sm font-medium mb-2 text-blue-300 flex items-center gap-1.5">💡 提示:</h4>
      <p v-if="modeCurrent === 'text2sql'" class="mb-2 text-gray-400">
        数据库模式下，您可以尝试输入：
      </p>
      <ul v-if="modeCurrent === 'text2sql'" class="m-0 p-0 list-none">
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">"查询所有学生"</li>
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">
          "查询计算机学院的男生"
        </li>
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">"统计各学院人数"</li>
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">
          "插入X名2024级的学生"
        </li>
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">
          "删除所有2024级的学生"
        </li>
        <li class="py-1 text-gray-400 border-b border-dashed border-white/10">
          "查看计算机学院不同专业人数"
        </li>
        <li class="py-1 text-gray-400 border-b-0">"查看学校招生人数变化"</li>
      </ul>
      <p v-else-if="modeCurrent === 'focus'" class="mb-2 text-gray-400">
        纳西妲模式下，您可以询问任何复杂的问题，她会深度思考后给出答案。
      </p>
      <p v-else class="mb-2 text-gray-400">芙芙模式下，您可以和她聊天，分享您的日常。</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/counter'
import ModeSelector from './ModeSelector.vue'

const chatStore = useChatStore()

const modeCurrent = computed(() => {
  return chatStore.currentMode
})

const emit = defineEmits<{
  modeChange: [mode: 'chat' | 'focus' | 'text2sql']
}>()

const handleModeChange = (mode: 'chat' | 'focus' | 'text2sql') => {
  chatStore.setMode(mode)
  console.log('emit modeChange', mode)
  emit('modeChange', mode)
}
</script>

<style scoped>
/* 所有样式已移至模板中的class属性 */
</style>
