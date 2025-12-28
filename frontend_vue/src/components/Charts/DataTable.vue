<template>
  <div class="my-6">
    <table class="w-full border-collapse my-6 text-sm shadow-md rounded-lg overflow-hidden">
      <thead>
        <tr>
          <th
            v-for="key in headers"
            :key="key"
            class="bg-gray-600 text-white font-semibold py-3 px-4 text-left"
          >
            {{ key }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in data" :key="index">
          <td v-for="key in headers" :key="key" class="py-3 px-4 border-b border-gray-100 bg-white">
            {{ formatValue(row[key]) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  data: any[]
}

const props = defineProps<Props>()

// 获取表头
const headers = computed(() => {
  if (!props.data || props.data.length === 0) return []
  return Object.keys(props.data[0])
})

// 格式化单元格值
const formatValue = (value: any) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') return value.toLocaleString()
  if (typeof value === 'boolean') return value ? '是' : '否'
  return value
}
</script>

<style scoped>
/* 所有样式已移至模板中的class属性 */
</style>
