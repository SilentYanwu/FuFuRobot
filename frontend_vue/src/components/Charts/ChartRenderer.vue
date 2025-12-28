<template>
  <div class="w-full h-80 my-6 bg-white rounded-xl shadow-lg p-4 border border-gray-100">
    <v-chart
      :option="chartOption"
      :loading="loading"
      :loading-options="loadingOptions"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, ScatterChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { useCharts } from '@/composables/useCharts'

interface Props {
  data: any[]
  chartType: string
  config?: any
}

const props = withDefaults(defineProps<Props>(), {
  config: () => ({}),
})

// 注册必要的组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const { generateChartOption, preprocessChartData } = useCharts()

const loading = ref(true)

// 根据类型和配置生成图表选项
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) return {}

  const processedData = preprocessChartData(props.data, props.chartType)
  return generateChartOption(processedData, props.chartType, props.config)
})

// 图表加载配置
const loadingOptions = {
  text: '图表加载中...',
  color: '#3498db',
  textColor: '#000',
  maskColor: 'rgba(255, 255, 255, 0.8)',
  zlevel: 0,
}

// 监听数据变化
watch(
  () => props.data,
  () => {
    loading.value = false
  },
  { immediate: true },
)
</script>

<style scoped>
/* 所有样式已移至模板中的class属性 */
</style>
