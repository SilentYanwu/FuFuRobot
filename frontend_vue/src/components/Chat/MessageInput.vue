<template>
  <div class="input-box">
    <input
      v-model="inputText"
      type="text"
      :placeholder="placeholder"
      @keypress="handleKeyPress"
      autocomplete="off"
      class="flex-1"
    />
    <button @click="handleSend" :disabled="!inputText.trim() || isLoading">发送</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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

const handleSend = () => {
  if (!inputText.value.trim() || props.isLoading) return

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
