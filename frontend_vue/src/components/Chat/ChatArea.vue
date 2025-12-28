<template>
  <div class="chat-area">
    <div class="chat-header">芙芙</div>

    <MessageList ref="messageListRef" />

    <MessageInput
      :placeholder="inputPlaceholder"
      :isLoading="isLoading"
      @send="handleSendMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/counter'
import { useChat } from '@/composables/useChat'
import { storeToRefs } from 'pinia'

import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'

const chatStore = useChatStore()
const { isLoading } = chatStore
const { currentMode } = storeToRefs(chatStore)

const { messagesContainer, sendMessage, getInputPlaceholder, showWelcomeMessage } = useChat()

const messageListRef = ref<InstanceType<typeof MessageList> | null>(null)
const inputPlaceholder = ref('')

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
