<template>
  <div class="input-box inline-flex items-center gap-2">
    <button
      class="mic-btn flex items-center justify-center p-2 rounded-full transition-colors"
      :class="
        isRecording
          ? 'bg-red-500 text-white animate-pulse'
          : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
      "
      @click="toggleRecording"
      :title="isRecording ? '点击停止说话' : '点击开始说话'"
    >
      <span v-if="isRecording">⏹️</span>
      <span v-else>🎤</span>
    </button>

    <input
      v-model="inputText"
      type="text"
      :placeholder="isRecording ? '请说话，正在聆听...' : placeholder"
      @keypress="handleKeyPress"
      autocomplete="off"
      class="flex-1"
      :disabled="isRecording"
    />
    <button @click="handleSend" :disabled="!inputText.trim() || isLoading || isRecording">
      发送
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/counter'

interface Props {
  placeholder: string
  isLoading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  send: [text: string]
}>()

const inputText = ref('')

// ====== 语音识别 (STT) 逻辑 ======
const isRecording = ref(false)
let recognition: any = null

const initRecognition = () => {
  // 检查浏览器是否支持 Web Speech API
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('当前浏览器不支持语音识别 API')
    return false
  }

  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN' // 识别中文
  recognition.interimResults = true // 允许返回临时结果，实现打字机效果
  recognition.continuous = false // 说话停止自动结束

  recognition.onresult = (event: any) => {
    let interimTranscript = ''
    let finalTranscript = ''

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript
      } else {
        interimTranscript += event.results[i][0].transcript
      }
    }

    // 更新输入框内容，如果是最终结果，就直接赋值
    if (finalTranscript) {
      inputText.value = finalTranscript
    } else if (interimTranscript) {
      inputText.value = interimTranscript
    }
  }

  recognition.onerror = (event: any) => {
    console.error('Speech recognition error', event.error)
    isRecording.value = false
  }

  recognition.onend = () => {
    isRecording.value = false
  }

  return true
}

const toggleRecording = () => {
  if (isRecording.value) {
    recognition?.stop()
    isRecording.value = false
  } else {
    if (!recognition) {
      if (!initRecognition()) {
        alert('您的浏览器不支持语音识别功能，请尝试使用 Chrome 或 Edge 浏览器。')
        return
      }
    }
    // 录音前清空当前输入
    inputText.value = ''
    try {
      recognition.start()
      isRecording.value = true
    } catch (e) {
      console.error('启动语音识别失败:', e)
    }
  }
}

// 组件卸载时停止录音
onUnmounted(() => {
  if (isRecording.value && recognition) {
    recognition.stop()
  }
})
// ====== 语音识别 (STT) 逻辑结束 ======

const handleSend = () => {
  if (!inputText.value.trim() || props.isLoading || isRecording.value) return

  const text = inputText.value
  inputText.value = ''

  emit('send', text)
}

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<style scoped>
.mic-btn {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.mic-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
