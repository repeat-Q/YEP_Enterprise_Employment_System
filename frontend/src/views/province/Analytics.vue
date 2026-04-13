<template>
  <div>
    <el-card header="就业趋势分析" style="margin-bottom:20px">
      <div style="display:flex;gap:12px;margin-bottom:16px">
        <el-select v-model="year" style="width:120px" @change="loadTrend">
          <el-option v-for="y in years" :key="y" :value="y" :label="y+'年'" />
        </el-select>
      </div>
      <div ref="trendChartRef" style="height:350px" />
    </el-card>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="就业结构分析">
          <div ref="pieChartRef" style="height:300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="数据汇总">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="企业总数">{{ summary.total_enterprises }}</el-descriptions-item>
            <el-descriptions-item label="报表总数">{{ summary.total_reports }}</el-descriptions-item>
            <el-descriptions-item label="待市级审核">{{ summary.pending_city_review }}</el-descriptions-item>
            <el-descriptions-item label="待省级审批">{{ summary.pending_province_review }}</el-descriptions-item>
            <el-descriptions-item label="已批准就业总数">{{ summary.total_employed }}</el-descriptions-item>
            <el-descriptions-item label="已批准失业总数">{{ summary.total_unemployed }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import http from '@/utils/http'

const year = ref(new Date().getFullYear())
const years = [2024, 2025, 2026, 2027]
const trendChartRef = ref()
const pieChartRef = ref()
const summary = ref({})
let trendChart, pieChart

const loadTrend = async () => {
  const data = await http.get(`/data/stats/trend?year=${year.value}`)
  const months = data.trend.map(d => d.month + '月')
  const employed = data.trend.map(d => d.employed)
  const unemployed = data.trend.map(d => d.unemployed)
  const newEmp = data.trend.map(d => d.new_employed)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['在职人数', '失业人数', '新增就业'] },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value' },
    series: [
      { name: '在职人数', type: 'bar', data: employed, itemStyle: { color: '#409eff' } },
      { name: '失业人数', type: 'bar', data: unemployed, itemStyle: { color: '#f56c6c' } },
      { name: '新增就业', type: 'line', data: newEmp, itemStyle: { color: '#67c23a' } },
    ]
  })
}

onMounted(async () => {
  trendChart = echarts.init(trendChartRef.value)
  pieChart = echarts.init(pieChartRef.value)

  summary.value = await http.get('/data/stats/summary')

  const pieData = [
    { name: '在职人员', value: summary.value.total_employed },
    { name: '失业人员', value: summary.value.total_unemployed },
  ]
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: pieData,
      emphasis: { itemStyle: { shadowBlur: 10 } }
    }]
  })

  await loadTrend()
})
</script>
