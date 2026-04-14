<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover">
          <div style="display:flex;align-items:center;gap:16px">
            <el-icon :style="{color:card.color,fontSize:'32px'}"><component :is="card.icon" /></el-icon>
            <div>
              <div style="font-size:28px;font-weight:700">{{ card.value }}</div>
              <div style="font-size:13px;color:#909399">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card header="待审批报表" style="margin-top:20px">
      <el-table :data="pendingReports" stripe v-loading="loading">
        <el-table-column label="企业名称" min-width="180">
          <template #default="{row}">{{ row.enterprise_name || '企业'+row.enterprise_id }}</template>
        </el-table-column>
        <el-table-column label="报告年月" width="120">
          <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
        </el-table-column>
        <el-table-column prop="current_employed" label="在职人数" width="100" />
        <el-table-column prop="unemployed_count" label="失业人数" width="100" />
        <el-table-column label="市级审核时间" width="180">
          <template #default="{row}">{{ (row.city_review_time||'').slice(0,19).replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button type="primary" size="small" @click="$router.push('/province/approve/'+row.id)">审批</el-button>
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
  { label: '待省级审批', value: 0, icon: 'Stamp', color: '#e6a23c' },
  { label: '今日已审批', value: 0, icon: 'Checked', color: '#67c23a' },
  { label: '总就业人数', value: 0, icon: 'User', color: '#409eff' },
  { label: '总失业人数', value: 0, icon: 'Warning', color: '#f56c6c' },
])

onMounted(async () => {
  loading.value = true
  try {
    const [reports, stats] = await Promise.all([
      http.get('/data/province/reports').catch(() => []),
      http.get('/data/stats/summary').catch(() => ({}))
    ])
    pendingReports.value = Array.isArray(reports) ? reports : []
    statCards.value[0].value = stats.pending_province_review || 0
    statCards.value[1].value = (stats.today_province_reviewed || 0)
    statCards.value[2].value = stats.total_employed || 0
    statCards.value[3].value = stats.total_unemployed || 0
  } catch (e) {
    console.error('加载首页数据失败:', e)
  } finally { loading.value = false }
})
</script>
