<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">⚙️ 系统配置</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <div v-if="isLoading" class="loading-state">正在读取配置...</div>

        <form v-else @submit.prevent="saveConfig" class="config-form">
          <div class="form-group row">
            <label>DeepSeek API Key</label>
            <div class="password-input-wrapper">
              <input
                v-model="config.DEEPSEEK_API_KEY"
                :type="showApiKey ? 'text' : 'password'"
                placeholder="sk-..."
              />
              <button
                type="button"
                class="visibility-toggle"
                @click="showApiKey = !showApiKey"
                :title="showApiKey ? '隐藏密钥' : '显示密钥'"
              >
                {{ showApiKey ? '🫣' : '👁️' }}
              </button>
            </div>
            <small class="help-text">如果未设置，则必须在后端 .env 中配置</small>
          </div>

          <div class="form-group row">
            <label>API URL</label>
            <input v-model="config.DEEPSEEK_API_URL" type="text" />
          </div>

          <div class="form-group row">
            <label>AI 模型</label>
            <input v-model="config.DEEPSEEK_MODEL" type="text" />
          </div>

          <div class="form-group row">
            <label>数据库名称</label>
            <input v-model="config.DB_NAME" type="text" />
          </div>

          <div class="form-group row double-col">
            <div class="sub-col">
              <label>后端 Host</label>
              <input v-model="config.BACKEND_HOST" type="text" />
            </div>
            <div class="sub-col">
              <label>后端 Port</label>
              <input v-model.number="config.BACKEND_PORT" type="number" />
            </div>
          </div>

          <div class="form-group row double-col">
            <div class="sub-col">
              <label>前端 Host</label>
              <input v-model="config.FRONTEND_HOST" type="text" />
            </div>
            <div class="sub-col">
              <label>前端 Port</label>
              <input v-model.number="config.FRONTEND_PORT" type="number" />
            </div>
          </div>

          <div v-if="saveMessage" :class="['message', isError ? 'error' : 'success']">
            {{ saveMessage }}
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? '保存中...' : '保存配置' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const isLoading = ref(false)
const isSaving = ref(false)
const saveMessage = ref('')
const isError = ref(false)
const showApiKey = ref(false)

// 基础配置对象
const config = reactive({
  DEEPSEEK_API_KEY: '',
  DEEPSEEK_API_URL: '',
  DEEPSEEK_MODEL: '',
  DB_NAME: '',
  BACKEND_HOST: '',
  BACKEND_PORT: 8000,
  FRONTEND_HOST: '',
  FRONTEND_PORT: 8080,
})

// 读取配置
const loadConfig = async () => {
  isLoading.value = true
  saveMessage.value = ''

  try {
    const response = await fetch('http://127.0.0.1:8000/api/config')
    const result = await response.json()

    if (result.success && result.config) {
      Object.assign(config, result.config)
    } else {
      throw new Error('读取配置失败')
    }
  } catch (error) {
    console.error('获取配置失败:', error)
    saveMessage.value = '无法连接到服务器读取配置'
    isError.value = true
  } finally {
    isLoading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  isSaving.value = true
  saveMessage.value = ''
  isError.value = false

  try {
    const response = await fetch('http://127.0.0.1:8000/api/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ config }),
    })

    const result = await response.json()

    if (result.success) {
      saveMessage.value = '保存成功！部分配置可能需要重启后端才能生效。'
      setTimeout(() => {
        close()
      }, 2000)
    } else {
      throw new Error('保存配置失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    saveMessage.value = '无法连接到服务器保存配置'
    isError.value = true
  } finally {
    isSaving.value = false
  }
}

// 关闭模态框
const close = () => {
  saveMessage.value = ''
  emit('close')
}

// 监听弹窗打开，每次打开时拉取最新配置
watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      loadConfig()
    }
  },
)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.5);
}

.modal-title {
  margin: 0;
  font-size: 1.1em;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5em;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.loading-state {
  text-align: center;
  padding: 40px 0;
  color: #64748b;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group.row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.9em;
  font-weight: 500;
  color: #334155;
  margin-left: 4px;
}

.form-group input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(203, 213, 225, 0.8);
  background: rgba(255, 255, 255, 0.9);
  outline: none;
  transition: all 0.2s ease;
  font-size: 0.95em;
  color: #1e293b;
}

.form-group input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: #ffffff;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  flex: 1;
  width: 100%;
  padding-right: 40px;
}

.visibility-toggle {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
  opacity: 0.6;
  transition: opacity 0.2s;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.visibility-toggle:hover {
  opacity: 1;
}

.double-col {
  flex-direction: row !important;
  gap: 16px !important;
}

.sub-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.help-text {
  font-size: 0.8em;
  color: #94a3b8;
  margin-left: 4px;
}

.message {
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9em;
  text-align: center;
}

.message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.modal-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: rgba(241, 245, 249, 0.8);
  color: #475569;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
