<template>
  <div
    class="message"
    :class="[role, { 'user-message': role === 'user', 'flex-row-reverse': role === 'user' }]"
  >
    <Avatar :role="role" />
    <div class="message-content">
      <div class="bubble">
        <!-- 思考模式 -->
        <template v-if="type === 'thinking'"> </template>

        <!-- 回答模式 -->
        <template v-if="type === 'answer'">
          <details class="thinking-box" :open="!content" :class="{ completed: isCompleted }">
            <summary class="thinking-summary">
              {{ content === '' ? '🍃 纳西妲来帮忙了...' : '🍃 纳西妲思考完毕' }} :
            </summary>
            <div class="thinking-content">{{ thinking_content }}</div>
          </details>
          <div class="nahida-answer" v-if="content !== ''">
            <div class="nahida-badge">小吉祥草王的解答</div>
            <div class="markdown-content" v-html="renderMarkdown(content)"></div>
          </div>
        </template>

        <!-- 普通消息 -->
        <template v-else>
          <div v-if="html" class="markdown-content" v-html="html"></div>
          <div v-else class="message-text" v-html="content"></div>
        </template>

        <!-- SQL查询显示 -->
        <div v-if="sql" class="sql-query">
          <strong>执行的SQL查询:</strong><br />
          <code class="sql-code">{{ sql }}</code>
        </div>

        <!-- 操作结果 -->
        <div v-if="operationResult" class="operation-result success">
          <div>✅ v-html="content"</div>
          <div class="operation-details">
            <small>操作详情: {{ JSON.stringify(operationResult) }}</small>
          </div>
        </div>

        <!-- 数据表格 -->
        <DataTable v-if="data && data.length > 0 && !operationResult" :data="data" />

        <!-- 图表 -->
        <ChartRenderer
          v-if="chartType && chartType !== 'none' && data && data.length > 0"
          :data="data"
          :chart-type="chartType"
          :config="chartConfig"
        />

        <!-- 时间戳 -->
        <div class="message-time">{{ formattedTime }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import Avatar from '@/components/Common/Avatar.vue'
import DataTable from '@/components/Charts/DataTable.vue'
import ChartRenderer from '@/components/Charts/ChartRenderer.vue'
import type { Message } from '@/types'

interface Props {
  message: Message
}

const props = defineProps<Props>()

// 使用计算属性确保响应式更新
const content = computed(() => props.message.content)
const thinking_content = computed(() => props.message.thinking_content)
const role = computed(() => props.message.role)
const type = computed(() => props.message.type)
const html = computed(() => props.message.html)
const sql = computed(() => props.message.sql)
const data = computed(() => props.message.data)
const chartType = computed(() => props.message.chartType)
const chartConfig = computed(() => props.message.chartConfig)
const operationResult = computed(() => props.message.operationResult)
const timestamp = computed(() => props.message.timestamp)

// 格式化时间
const formattedTime = computed(() => {
  // timestamp已经是Date对象，直接使用
  return timestamp.value.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
})

// 渲染Markdown
const renderMarkdown = (text: string) => {
  return marked.parse(text)
}

const isCompleted = computed(() => type === 'answer')
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-content {
  flex: 1;
}

/* SQL 查询展示框 */
:deep(.sql-query) {
  margin: 1em 0;
  padding: 15px;
  background: #f8fafc;
  border-left: 4px solid #3498db;
  border-radius: 8px;
}

:deep(.sql-code) {
  display: block;
  margin-top: 8px;
  padding: 12px;
  background: #1a202c;
  color: #81e6d9;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 0.9em;
  overflow-x: auto;
  white-space: pre-wrap;
}

:deep(.nahida-badge) {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  color: #15803d;
  background: #dcfce7;
  padding: 4px 10px;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #bbf7d0;
}

:deep(.nahida-answer .markdown-content strong) {
  color: #052e16;
  background: linear-gradient(120deg, rgba(134, 239, 172, 0.4) 0%, rgba(134, 239, 172, 0.1) 100%);
}

:deep(.thinking-box) {
  margin-bottom: 20px;
  border-radius: 8px;
  background: #f6fffa;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border-left: 3px solid #bbf7d0;
  border-left-color: #4ade80;
}

:deep(.thinking-box summary) {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
  background: transparent;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
  user-select: none;
  outline: none;
}

:deep(.thinking-content) {
  padding: 15px 20px;
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  max-height: 300px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.5);
  white-space: pre-wrap;
}
</style>
