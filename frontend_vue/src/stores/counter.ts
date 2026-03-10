import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Message, ChatMode } from '@/types'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref<Message[]>([
    {
      id: '1',
      content: '你好！我是芙宁娜。',
      role: 'ai',
      timestamp: new Date(),
    },
  ])

  const currentMode = ref<ChatMode['id']>('chat')
  const isLoading = ref(false)

  // 聊天模式列表
  const chatModes: ChatMode[] = [
    { id: 'chat', name: '芙芙', icon: '💬', description: '普通聊天模式' },
    { id: 'focus', name: '纳西妲（附体芙芙）', icon: '🍃', description: '深度思考模式' },
    { id: 'text2sql', name: '数据库操作', icon: '📊', description: '数据库查询与操作' },
  ]

  // 操作
  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    // 生成日期部分 YYYYMMDD
    const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    // 生成4位随机数
    const randomNum = Math.floor(Math.random() * 10000)
      .toString()
      .padStart(4, '0')

    const newMessage: Message = {
      ...message,
      id: `${dateStr}${randomNum}`,
      timestamp: new Date(),
    }
    messages.value.push(newMessage)

    return newMessage.id
  }

  const setMode = (mode: ChatMode['id']) => {
    currentMode.value = mode
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const clearMessages = () => {
    messages.value = []
  }

  const isAutoTTSEnabled = ref(true)

  const toggleAutoTTS = () => {
    isAutoTTSEnabled.value = !isAutoTTSEnabled.value
  }

  return {
    messages,
    currentMode,
    isLoading,
    chatModes,
    isAutoTTSEnabled,
    addMessage,
    setMode,
    setLoading,
    clearMessages,
    toggleAutoTTS,
  }
})
