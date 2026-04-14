<template>
  <div>
    <el-card header="就业趋势分析" style="margin-bottom:20px">
      <div style="display:flex;gap:12px;margin-bottom:16px">
        <el-select v-model="year" style="width:120px" @change="loadTrend">
          <el-option v-for="y in years" :key="y" :value="y" :label="y+'年'" />
        </el-select>
      </div>
      <div v-if="trendEmpty" style="text-align:center;padding:60px 0;color:#909399">
        <el-icon style="font-size:48px;color:#dcdfe6"><TrendCharts /></el-icon>
        <p style="margin-top:12px">暂无{{ year }}年趋势数据</p>
        <p style="font-size:13px;color:#c0c4cc">报表数据提交后将显示趋势图</p>
      </div>
      <div v-else ref="trendChartRef" style="height:350px" />
    </el-card>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="就业结构分析">
          <div v-if="pieEmpty" style="text-align:center;padding:60px 0;color:#909399">
            <p>暂无就业数据</p>
            <p style="font-size:13px;color:#c0c4cc">报表数据提交后将显示结构图</p>
          </div>
          <div v-else ref="pieChartRef" style="height:300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="数据汇总">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="企业总数">{{ summary.total_enterprises || 0 }}</el-descriptions-item>
            <el-descriptions-item label="报表总数">{{ summary.total_reports || 0 }}</el-descriptions-item>
            <el-descriptions-item label="待市级审核">
              <el-tag type="warning">{{ summary.pending_city_review || 0 }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="待省级审批">
              <el-tag type="warning">{{ summary.pending_province_review || 0 }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="就业人数总计">{{ summary.total_employed || 0 }}</el-descriptions-item>
            <el-descriptions-item label="失业人数总计">{{ summary.total_unemployed || 0 }}</el-descriptions-item>
            <el-descriptions-item label="已批准报表数">{{ summary.approved_reports || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '@/utils/http'

const year = ref(new Date().getFullYear())
const years = [2024, 2025, 2026, 2027]
const trendChartRef = ref()
const pieChartRef = ref()
const summary = ref({})
const trendEmpty = ref(false)
const pieEmpty = ref(false)
let trendChart = null
let pieChart = null

// 窗口大小变化时自适应
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})

const loadTrend = async () => {
  try {
    const data = await http.get(`/data/stats/trend?year=${year.value}`)
    const trend = data.trend || []
    trendEmpty.value = trend.length === 0
    if (trendEmpty.value) return
    
    await nextTick()
    if (!trendChart && trendChartRef.value) {
      trendChart = echarts.init(trendChartRef.value)
    }
    if (!trendChart) return

    const months = trend.map(d => d.month + '月')
    const employed = trend.map(d => d.employed)
    const unemployed = trend.map(d => d.unemployed)
    const newEmp = trend.map(d => d.new_employed)

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
    }, true)
  } catch (e) {
    console.error('加载趋势数据失败:', e)
    trendEmpty.value = true
  }
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  
  try {
    summary.value = await http.get('/data/stats/summary')

    const hasPieData = (summary.value.total_employed > 0 || summary.value.total_unemployed > 0)
    pieEmpty.value = !hasPieData
    
    if (hasPieData) {
      await nextTick()
      if (pieChartRef.value) {
        pieChart = echarts.init(pieChartRef.value)
        const pieData = [
          { name: '在职人员', value: summary.value.total_employed || 0 },
          { name: '失业人员', value: summary.value.total_unemployed || 0 },
        ]
        pieChart.setOption({
          tooltip: { trigger: 'item' },
          legend: { bottom: 0 },
          series: [{
            type: 'pie', radius: ['40%', '70%'],
            data: pieData,
            emphasis: { itemStyle: { shadowBlur: 10 } }
          }]
        }, true)
      }
    }

    await loadTrend()
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
})
</script>
