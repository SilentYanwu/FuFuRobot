<template>
  <div class="chat-area">
    <div class="chat-header">
      <div class="header-actions">
        <!-- 全局自动语音开关 -->
        <button
          class="global-tts-toggle"
          @click="chatStore.toggleAutoTTS()"
          :title="chatStore.isAutoTTSEnabled ? '自动朗读：已开启' : '自动朗读：已关闭'"
          :class="{ 'is-active': chatStore.isAutoTTSEnabled }"
        >
          <span class="icon">{{ chatStore.isAutoTTSEnabled ? '🔊' : '🔇' }}</span>
          <span class="text">{{ chatStore.isAutoTTSEnabled ? '语音开' : '语音关' }}</span>
        </button>

        <!-- 设置按钮 -->
        <button class="settings-btn" @click="isSettingsOpen = true" title="系统配置">⚙️</button>
      </div>
    </div>

    <MessageList ref="messageListRef" />

    <MessageInput
      :placeholder="inputPlaceholder"
      :isLoading="isLoading"
      @send="handleSendMessage"
    />

    <SettingsModal :isOpen="isSettingsOpen" @close="isSettingsOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/counter'
import { useChat } from '@/composables/useChat'
import { storeToRefs } from 'pinia'

import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import SettingsModal from '@/components/Common/SettingsModal.vue'

const chatStore = useChatStore()
const { isLoading } = chatStore
const { currentMode } = storeToRefs(chatStore)

const { messagesContainer, sendMessage, getInputPlaceholder, showWelcomeMessage } = useChat()

const messageListRef = ref<InstanceType<typeof MessageList> | null>(null)
const inputPlaceholder = ref('')
const isSettingsOpen = ref(false)

// 处理发送消息
const handleSendMessage = (text: string) => {
  sendMessage(text)
}

// 初始化
onMounted(() => {
  // 连接消息容器引用
  if (messageListRef.value?.messagesContainer) {
    messagesContainer.value = messageListRef.value.messagesContainer
  }

  // 设置输入框占位符
  inputPlaceholder.value = getInputPlaceholder()

  // 显示欢迎消息
  showWelcomeMessage()
})

// 监听模式变化
watch(currentMode, () => {
  inputPlaceholder.value = getInputPlaceholder()
})
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  font-weight: bold;
  font-size: 1.2em;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.global-tts-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.85em;
  color: #6b7280;
}

.global-tts-toggle:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.global-tts-toggle.is-active {
  background: #ecfdf5;
  border-color: #a7f3d0;
  color: #059669;
}

.settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1.1em;
  color: #6b7280;
}

.settings-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: rotate(30deg);
}
</style>
