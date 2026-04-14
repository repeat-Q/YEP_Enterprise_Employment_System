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
          <div class="big-number blue">{{ stats.total_employed?.toLocaleString() || 0 }}</div>
          <div class="screen-card-sub">累计就业人数（人）</div>
          <el-divider />
          <div class="screen-card-title">失业人员</div>
          <div class="big-number red">{{ stats.total_unemployed?.toLocaleString() || 0 }}</div>
          <div class="screen-card-sub">累计失业人数（人）</div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="screen-card">
          <div class="screen-card-title">月度就业趋势</div>
          <div v-if="trendEmpty" style="text-align:center;padding:100px 0;color:#c0d4f0">
            <p>暂无趋势数据</p>
            <p style="font-size:12px;color:#8899aa">报表数据提交后将显示</p>
          </div>
          <div v-else ref="trendRef" style="height:320px" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="screen-card">
          <div class="screen-card-title">系统数据概览</div>
          <div class="kv-list">
            <div class="kv-item"><span>入库企业</span><span class="kv-val">{{ stats.total_enterprises || 0 }}</span></div>
            <div class="kv-item"><span>报表总数</span><span class="kv-val">{{ stats.total_reports || 0 }}</span></div>
            <div class="kv-item"><span>待市级审核</span><span class="kv-val orange">{{ stats.pending_city_review || 0 }}</span></div>
            <div class="kv-item"><span>待省级审批</span><span class="kv-val orange">{{ stats.pending_province_review || 0 }}</span></div>
            <div class="kv-item"><span>已归档报表</span><span class="kv-val green">{{ stats.approved_reports || 0 }}</span></div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import http from '@/utils/http'

const currentTime = ref('')
const stats = ref({})
const trendRef = ref()
const trendEmpty = ref(false)
let trendChart = null
let timer = null

const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

const handleResize = () => { trendChart?.resize() }

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  window.addEventListener('resize', handleResize)

  try {
    const [summaryData, trendData] = await Promise.all([
      http.get('/data/stats/summary').catch(() => ({})),
      http.get('/data/stats/trend').catch(() => ({ trend: [] }))
    ])
    stats.value = summaryData
    const trend = trendData.trend || []
    trendEmpty.value = trend.length === 0

    if (!trendEmpty.value) {
      await nextTick()
      if (trendRef.value) {
        trendChart = echarts.init(trendRef.value)
        trendChart.setOption({
          backgroundColor: 'transparent',
          tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', textStyle: { color: '#fff' } },
          legend: { data: ['在职人数', '失业人数', '新增就业'], textStyle: { color: '#c0d4f0' } },
          xAxis: { type: 'category', data: trend.map(d => d.month+'月'), axisLabel: { color: '#c0d4f0' } },
          yAxis: { type: 'value', axisLabel: { color: '#c0d4f0' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
          series: [
            { name: '在职人数', type: 'line', smooth: true, data: trend.map(d => d.employed),
              lineStyle: { color: '#00d4ff' }, areaStyle: { color: 'rgba(0,212,255,0.2)' } },
            { name: '失业人数', type: 'line', smooth: true, data: trend.map(d => d.unemployed),
              lineStyle: { color: '#ff6b6b' }, areaStyle: { color: 'rgba(255,107,107,0.2)' } },
            { name: '新增就业', type: 'bar', data: trend.map(d => d.new_employed),
              itemStyle: { color: 'rgba(103,194,58,0.6)' } },
          ]
        }, true)
      }
    }
  } catch (e) {
    console.error('加载数据失败:', e)
    trendEmpty.value = true
  }
})

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
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
