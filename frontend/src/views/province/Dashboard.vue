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

    <!-- 市级待审核报表 -->
    <el-card style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>📋 市级待审核报表</span>
          <el-tag type="warning">{{ cityReports.length }} 条</el-tag>
        </div>
      </template>
      <el-table :data="cityReports" stripe v-loading="loading" empty-text="暂无市级待审核报表">
        <el-table-column label="企业名称" min-width="180">
          <template #default="{row}">{{ row.enterprise_name || '企业'+row.enterprise_id }}</template>
        </el-table-column>
        <el-table-column label="报告年月" width="120">
          <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
        </el-table-column>
        <el-table-column prop="current_employed" label="在职人数" width="100" />
        <el-table-column prop="unemployed_count" label="失业人数" width="100" />
        <el-table-column label="状态" width="120" align="center">
          <template #default>
            <el-tag type="warning">待市级审核</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="170">
          <template #default="{row}">{{ (row.submit_time||'').slice(0,16).replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button type="warning" size="small" @click="$router.push('/province/approve/'+row.id)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 省级待审批报表 -->
    <el-card style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>📋 省级待审批报表</span>
          <el-tag>{{ provinceReports.length }} 条</el-tag>
        </div>
      </template>
      <el-table :data="provinceReports" stripe v-loading="loading" empty-text="暂无省级待审批报表">
        <el-table-column label="企业名称" min-width="180">
          <template #default="{row}">{{ row.enterprise_name || '企业'+row.enterprise_id }}</template>
        </el-table-column>
        <el-table-column label="报告年月" width="120">
          <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
        </el-table-column>
        <el-table-column prop="current_employed" label="在职人数" width="100" />
        <el-table-column prop="unemployed_count" label="失业人数" width="100" />
        <el-table-column label="状态" width="120" align="center">
          <template #default>
            <el-tag>待省级审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="市级审核时间" width="170">
          <template #default="{row}">{{ (row.city_review_time||'').slice(0,16).replace('T',' ') }}</template>
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

const cityReports = ref([])
const provinceReports = ref([])
const loading = ref(false)
const statCards = ref([
  { label: '市级待审核', value: 0, icon: 'Document', color: '#e6a23c' },
  { label: '省级待审批', value: 0, icon: 'Stamp', color: '#409eff' },
  { label: '总就业人数', value: 0, icon: 'User', color: '#67c23a' },
  { label: '总失业人数', value: 0, icon: 'Warning', color: '#f56c6c' },
])

onMounted(async () => {
  loading.value = true
  try {
    const [cityRes, provinceRes, stats] = await Promise.all([
      http.get('/data/province/reports?status_filter=city_review').catch(() => []),
      http.get('/data/province/reports?status_filter=province_review').catch(() => []),
      http.get('/data/stats/summary').catch(() => ({}))
    ])
    cityReports.value = Array.isArray(cityRes) ? cityRes : []
    provinceReports.value = Array.isArray(provinceRes) ? provinceRes : []
    statCards.value[0].value = stats.pending_city_review || 0
    statCards.value[1].value = stats.pending_province_review || 0
    statCards.value[2].value = stats.total_employed || 0
    statCards.value[3].value = stats.total_unemployed || 0
  } catch (e) {
    console.error('加载首页数据失败:', e)
  } finally { loading.value = false }
})
</script>
