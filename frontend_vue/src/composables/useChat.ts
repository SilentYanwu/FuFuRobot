import { ref, nextTick } from 'vue'
import { useChatStore } from '@/stores/counter'
import { useChatApi } from './useApi'
import { useCharts } from './useCharts'
import type { Message, StreamData } from '@/types'

export function useChat() {
  const chatStore = useChatStore()
  const { sendChatMessage, sendChatStream } = useChatApi()
  const { generateChartOption, preprocessChartData } = useCharts()

  const messagesContainer = ref<HTMLElement | null>(null)

  // 发送消息
  const sendMessage = async (text: string) => {
    if (!text.trim()) return

    // 添加用户消息
    chatStore.addMessage({
      content: text,
      role: 'user',
    })

    const mode = chatStore.currentMode

    // 处理不同模式的消息
    if (mode === 'focus') {
      await handleStreamFocusMode(text)
    } else {
      chatStore.setLoading(true)
      try {
        const resData = await sendChatMessage(text, mode)
        handleAIResponse(resData)
      } catch (error) {
        handleError(error as Error)
      } finally {
        chatStore.setLoading(false)
      }
    }

    // 滚动到底部
    await scrollToBottom()
  }

  // 处理流式聚焦模式的聊天响应
  const handleStreamFocusMode = async (text: string) => {
    // 添加AI消息占位
    const messageId = chatStore.addMessage({
      content: '',
      role: 'ai',
      type: 'thinking',
    })

    let fullThinking = ''
    let fullAnswer = ''

    await sendChatStream(
      text,
      'focus',
      'default',
      (data: StreamData) => {
        console.log(data)
        if (data.type === 'thinking') {
          fullThinking += data.content
          updateMessage(messageId, {
            thinking_content: fullThinking,
            type: 'answer',
          })
        } else if (data.type === 'answer') {
          fullAnswer += data.content
          updateMessage(messageId, {
            content: fullAnswer,
            type: 'answer',
          })
        } else if (data.type === 'error') {
          updateMessage(messageId, {
            content:
              (fullAnswer || '') + `<br><span style="color:red">[错误: ${data.content}]</span>`,
            type: 'answer',
          })
        }

        scrollToBottom()
      },
      () => {
        if (!fullAnswer) {
          updateMessage(messageId, {
            content: fullThinking,
            type: 'thinking',
            html: `<div class="thinking-summary">🍃 思考结束 (无回答)</div>`,
          })
        }
      },
      (error) => {
        updateMessage(messageId, {
          content:
            (fullAnswer || '') + `<br><span style="color:red">[网络错误: ${error.message}]</span>`,
          type: 'answer',
        })
      },
    )
  }

  // 处理AI响应
  const handleAIResponse = (resData: any) => {
    const message: Partial<Message> = {
      content: resData.html || resData.text || '收到无内容的消息',
      role: 'ai',
      data: resData.data,
      sql: resData.sql,
      chartType: resData.chart_type,
      chartConfig: resData.chart_config,
      operationResult: resData.operation_result,
    }

    chatStore.addMessage(message)
  }

  // 更新消息
  const updateMessage = (messageId: string, updates: Partial<Message>) => {
    const messageIndex = chatStore.messages.findIndex((msg) => msg.id === messageId)
    if (messageIndex !== -1) {
      // 创建一个新对象，合并原有消息和更新内容，确保Vue能检测到变化
      const updatedMessage = { ...chatStore.messages[messageIndex], ...updates }
      // 使用数组的splice方法触发响应式更新
      chatStore.messages.splice(messageIndex, 1, updatedMessage)
      console.log(`更新消息 ${messageId} 的内容为`)
      console.log(updates)
    } else {
      console.warn(`未找到ID为 ${messageId} 的消息`)
    }
  }

  // 处理错误
  const handleError = (error: Error) => {
    chatStore.addMessage({
      content: `连接服务器失败，请确认后端服务已运行。错误: ${error.message}`,
      role: 'ai',
    })
  }

  // 滚动到底部
  const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTo({
        top: messagesContainer.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  }

  // 切换模式
  const switchMode = (mode: 'chat' | 'focus' | 'text2sql') => {
    chatStore.setMode(mode)
  }

  // 获取输入框占位符
  const getInputPlaceholder = () => {
    const mode = chatStore.currentMode

    switch (mode) {
      case 'chat':
        return '和芙芙聊天，分享你的日常...'
      case 'focus':
        return '🍃 纳西妲：请告诉我你想要了解的世间真理吧...'
      case 'text2sql':
        return '请输入数据查询指令，如：查询所有学生...'
      default:
        return '请输入您的指令...'
    }
  }

  // 显示欢迎消息
  const showWelcomeMessage = () => {
    setTimeout(() => {
      chatStore.addMessage({
        content: `您好！我是芙芙。QAQ我是您的聆听者，是您的小伙伴，还是您的好朋友,o(*￣▽￣*)ブ。

        如果问我很复杂的事情，我就会呼叫纳西妲来帮忙哦~(≧▽≦)/~

        而且呀，我可以帮助您完成以下任务：
        增删改查学生的数据
        生成统计图表

        请选择左侧的模式开始使用！`,
        role: 'ai',
      })
    }, 500)
  }

  return {
    messagesContainer,
    sendMessage,
    switchMode,
    getInputPlaceholder,
    showWelcomeMessage,
    scrollToBottom,
  }
}
