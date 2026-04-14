<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :style="{color:card.color,fontSize:'32px'}"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card header="待审核报表" style="margin-top:20px">
      <el-table :data="pendingReports" stripe v-loading="loading">
        <el-table-column label="企业名称" min-width="180">
          <template #default="{row}">{{ row.enterprise_name || '企业'+row.enterprise_id }}</template>
        </el-table-column>
        <el-table-column label="报告年月" width="120">
          <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
        </el-table-column>
        <el-table-column prop="current_employed" label="在职人数" width="100" />
        <el-table-column prop="unemployed_count" label="失业人数" width="100" />
        <el-table-column label="提交时间" width="180">
          <template #default="{row}">{{ (row.submit_time||'').slice(0,19).replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" type="primary" @click="$router.push('/city/review/'+row.id)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http'

const pendingReports = ref([])
const loading = ref(false)
const statCards = ref([
  { label: '待审核', value: 0, icon: 'Clock', color: '#e6a23c' },
  { label: '今日已审核', value: 0, icon: 'Checked', color: '#67c23a' },
  { label: '本月审核总数', value: 0, icon: 'Document', color: '#409eff' },
  { label: '退回数量', value: 0, icon: 'RefreshLeft', color: '#f56c6c' },
])

onMounted(async () => {
  loading.value = true
  try {
    // 并行加载待审核报表和统计数据
    const [reports, stats] = await Promise.all([
      http.get('/data/city/reports').catch(() => []),
      http.get('/data/stats/summary').catch(() => ({}))
    ])
    pendingReports.value = Array.isArray(reports) ? reports : []
    
    // 更新统计卡片
    statCards.value[0].value = stats.pending_city_review || pendingReports.value.length
    statCards.value[1].value = (stats.today_city_reviewed || 0)
    statCards.value[2].value = (stats.month_city_reviewed || 0)
    statCards.value[3].value = stats.city_rejected || 0
  } catch (e) {
    console.error('加载市级首页失败:', e)
  } finally { loading.value = false }
})
</script>

<style scoped>
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
</style>
