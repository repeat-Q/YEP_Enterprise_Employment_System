<template>
  <div class="data-screen" ref="screenRef">
    <div class="screen-header">
      <h1>云南省企业就业失业数据采集系统</h1>
      <div class="screen-time">{{ currentTime }}</div>
    </div>
    <el-row :gutter="16" class="screen-body">
      <el-col :span="6">
        <div class="screen-card">
          <div class="screen-card-title">全省就业概况</div>
          <div class="big-number blue">{{ stats.total_employed?.toLocaleString() }}</div>
          <div class="screen-card-sub">累计就业人数（人）</div>
          <el-divider />
          <div class="screen-card-title">失业人员</div>
          <div class="big-number red">{{ stats.total_unemployed?.toLocaleString() }}</div>
          <div class="screen-card-sub">累计失业人数（人）</div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="screen-card">
          <div class="screen-card-title">月度就业趋势</div>
          <div ref="trendRef" style="height:320px" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="screen-card">
          <div class="screen-card-title">系统数据概览</div>
          <div class="kv-list">
            <div class="kv-item"><span>入库企业</span><span class="kv-val">{{ stats.total_enterprises }}</span></div>
            <div class="kv-item"><span>报表总数</span><span class="kv-val">{{ stats.total_reports }}</span></div>
            <div class="kv-item"><span>待市级审核</span><span class="kv-val orange">{{ stats.pending_city_review }}</span></div>
            <div class="kv-item"><span>待省级审批</span><span class="kv-val orange">{{ stats.pending_province_review }}</span></div>
            <div class="kv-item"><span>已归档报表</span><span class="kv-val green">{{ stats.approved_reports }}</span></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '@/utils/http'

const currentTime = ref('')
const stats = ref({})
const trendRef = ref()
let trendChart, timer

const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  trendChart = echarts.init(trendRef.value)

  stats.value = await http.get('/data/stats/summary')
  const trendData = await http.get('/data/stats/trend')

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', textStyle: { color: '#fff' } },
    legend: { data: ['在职人数', '失业人数'], textStyle: { color: '#c0d4f0' } },
    xAxis: { type: 'category', data: trendData.trend.map(d => d.month+'月'), axisLabel: { color: '#c0d4f0' } },
    yAxis: { type: 'value', axisLabel: { color: '#c0d4f0' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    series: [
      { name: '在职人数', type: 'line', smooth: true, data: trendData.trend.map(d => d.employed),
        lineStyle: { color: '#00d4ff' }, areaStyle: { color: 'rgba(0,212,255,0.2)' } },
      { name: '失业人数', type: 'line', smooth: true, data: trendData.trend.map(d => d.unemployed),
        lineStyle: { color: '#ff6b6b' }, areaStyle: { color: 'rgba(255,107,107,0.2)' } },
    ]
  })
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.data-screen { background: #0a1628; min-height: 100vh; padding: 20px; color: white; }
.screen-header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid rgba(0,212,255,0.3); padding-bottom: 16px; }
.screen-header h1 { font-size: 28px; color: #00d4ff; margin: 0; }
.screen-time { color: #c0d4f0; font-size: 14px; margin-top: 6px; }
.screen-card { background: rgba(0,100,200,0.15); border: 1px solid rgba(0,212,255,0.2);
  border-radius: 8px; padding: 16px; height: 100%; }
.screen-card-title { font-size: 14px; color: #c0d4f0; margin-bottom: 8px; }
.screen-card-sub { font-size: 12px; color: #8899aa; }
.big-number { font-size: 36px; font-weight: 700; }
.big-number.blue { color: #00d4ff; }
.big-number.red { color: #ff6b6b; }
.kv-list { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; }
.kv-item { display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.kv-val { font-size: 18px; font-weight: 700; color: #00d4ff; }
.kv-val.orange { color: #ffa500; }
.kv-val.green { color: #67c23a; }
</style>
