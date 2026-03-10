import { ref } from 'vue'

export const audioState = ref<'idle' | 'loading' | 'playing'>('idle')
let audioPlayer: HTMLAudioElement | null = null

/**
 * 处理 TTS 文本，去除非语音内容，转化表情包
 * @param text 原始文本
 * @returns 处理后的适合朗读的文本
 */
const processTextForTTS = (text: string): string => {
  if (!text) return ''
  let processedText = text

  // 1. 去除 HTML 标签和多余符号
  processedText = processedText.replace(/<[^>]*>?/gm, '')
  processedText = processedText.replace(/\*/g, '') // 移除 Markdown 的星号

  // 1.5 移除各种 Emoji 表情符号 (使用 Unicode 范围)
  processedText = processedText.replace(/[\u{1F600}-\u{1F64F}]/gu, '') // Emoticons
  processedText = processedText.replace(/[\u{1F300}-\u{1F5FF}]/gu, '') // Misc Symbols and Pictographs
  processedText = processedText.replace(/[\u{1F680}-\u{1F6FF}]/gu, '') // Transport and Map
  processedText = processedText.replace(/[\u{1F700}-\u{1F77F}]/gu, '') // Alchemical Symbols
  processedText = processedText.replace(/[\u{1F780}-\u{1F7FF}]/gu, '') // Geometric Shapes Extended
  processedText = processedText.replace(/[\u{1F800}-\u{1F8FF}]/gu, '') // Supplemental Arrows-C
  processedText = processedText.replace(/[\u{1F900}-\u{1F9FF}]/gu, '') // Supplemental Symbols and Pictographs
  processedText = processedText.replace(/[\u{1FA00}-\u{1FA6F}]/gu, '') // Chess Symbols
  processedText = processedText.replace(/[\u{1FA70}-\u{1FAFF}]/gu, '') // Symbols and Pictographs Extended-A
  processedText = processedText.replace(/[\u{2600}-\u{26FF}]/gu, '') // Misc symbols (like ☀️)
  processedText = processedText.replace(/[\u{2700}-\u{27BF}]/gu, '') // Dingbats

  // 2. 将特定的复杂表情包替换为语音词汇
  // 必须在去除括号前执行，否则表情包里的括号会被删掉
  processedText = processedText.replace(/o\(\*￣▽￣\*\)ブ/g, '嘻嘻')
  processedText = processedText.replace(/\/\(ㄒoㄒ\)\/~~/g, '呜呜')
  processedText = processedText.replace(/O\(∩_∩\)O/gi, '嘻嘻')
  processedText = processedText.replace(/~\(≧▽≦\)~/g, '哇哦')
  processedText = processedText.replace(/QAQ/gi, '呜呜')

  // 3. 去除中文括号和英文括号及其内部的所有内容 (例如动作描述)
  processedText = processedText.replace(/（[^）]*）/g, '')
  processedText = processedText.replace(/\([^)]*\)/g, '')

  return processedText.trim()
}

export const playAudio = async (text: string, mode: string) => {
  // 提取纯文本并进行格式化 (移除动作和不需要朗读的表情包)
  const plainText = typeof text === 'string' ? processTextForTTS(text) : ''

  if (!plainText.trim()) return

  // 如果正在播放，则停止并重置
  if (audioState.value === 'playing' && audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
    audioState.value = 'idle'
  }

  try {
    audioState.value = 'loading'

    // 调用后端 TTS 接口
    const response = await fetch('http://127.0.0.1:8000/api/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: plainText,
        mode: mode,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 获取音频 Blob
    const blob = await response.blob()
    const audioUrl = URL.createObjectURL(blob)

    // 清理旧音频
    if (audioPlayer) {
      audioPlayer.pause()
      URL.revokeObjectURL(audioPlayer.src)
    }

    audioPlayer = new Audio(audioUrl)

    audioPlayer.onplay = () => {
      audioState.value = 'playing'
    }

    audioPlayer.onended = () => {
      audioState.value = 'idle'
    }

    audioPlayer.onerror = (e) => {
      console.error('Audio playback error', e)
      audioState.value = 'idle'
    }

    await audioPlayer.play()
  } catch (error) {
    console.error('Failed to play audio:', error)
    audioState.value = 'idle'
    console.warn('生成语音失败，请检查后端服务')
  }
}

export const stopAudio = () => {
  if (audioPlayer) {
    audioPlayer.pause()
    URL.revokeObjectURL(audioPlayer.src)
    audioPlayer = null
  }
  audioState.value = 'idle'
}
