import { useFetch } from '@vueuse/core'
import type { ApiResponse, StreamData } from '@/types'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

export function useChatApi() {
  // 发送普通聊天消息
  const sendChatMessage = async (message: string, mode: string) => {
    const { data, error } = await useFetch(`${API_BASE_URL}/chat`)
      .post({
        message,
        mode,
      })
      .json()

    if (error.value) {
      throw new Error(error.value)
    }

    return data.value as ApiResponse
  }

  const sendChatStream = async (
    message: string,
    mode: string,
    sessionId = 'default',
    onUpdate: (data: StreamData) => void,
    onDone: () => void,
    onError: (error: Error) => void,
  ) => {
    console.log('开始发送流式请求:', { message, mode, sessionId }) // 添加调试信息

    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          message,
          mode,
          session_id: sessionId,
        }),
      })

      console.log('收到响应:', response.status, response.statusText) // 添加调试信息

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      if (!reader) {
        throw new Error('无法获取响应流')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n') // 修正：应该是按换行符分割
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6)

            if (jsonStr.trim() === '[DONE]') {
              console.log('流式响应结束') // 添加调试信息
              onDone()
              return
            }

            try {
              const data = JSON.parse(jsonStr) as StreamData
              onUpdate(data)
            } catch (e) {
              console.warn('非JSON数据:', jsonStr)
            }
          }
        }
      }

      console.log('流式读取完成') // 添加调试信息
      onDone()
    } catch (error) {
      console.error('流式读取失败:', error)
      onError(error as Error)
    }
  }

  // 测试API连接
  const testConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      return response.ok
    } catch (error) {
      console.error('API连接测试失败:', error)
      return false
    }
  }

  return {
    sendChatMessage,
    sendChatStream,
    testConnection,
  }
}
