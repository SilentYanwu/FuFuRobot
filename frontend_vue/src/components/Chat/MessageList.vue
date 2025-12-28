
<template>
  <div ref="messagesContainer" class="messages-box">
    <Message 
      v-for="message in messages" 
      :key="message.id" 
      :message="message" 
    />

    <!-- 加载状态 -->
    <div v-if="isLoading" class="message ai">
      <Avatar role="ai" />
      <div class="message-content">
        <div class="bubble">
          <Loading />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/counter'
import Message from './Message.vue'
import Avatar from '@/components/Common/Avatar.vue'
import Loading from '@/components/Common/Loading.vue'

const chatStore = useChatStore()
const { messages, isLoading } = chatStore

// 消息容器引用，用于滚动控制
const messagesContainer = ref<HTMLElement | null>(null)

// 暴露给父组件
defineExpose({
  messagesContainer
})
</script>
