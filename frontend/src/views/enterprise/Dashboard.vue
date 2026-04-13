<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :style="{color: card.color, fontSize: '32px'}"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="16">
        <el-card header="最近填报记录">
          <el-table :data="recentReports" stripe>
            <el-table-column prop="report_year" label="年份" width="80" />
            <el-table-column prop="report_month" label="月份" width="80" :formatter="(r)=>r.report_month+'月'" />
            <el-table-column prop="current_employed" label="在职人数" />
            <el-table-column prop="status" label="状态">
              <template #default="{row}">
                <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{row}">
                <el-button link type="primary" @click="$router.push('/enterprise/report/'+row.id)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top:12px;text-align:right">
            <el-button type="primary" @click="$router.push('/enterprise/report/list')">查看全部</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card header="快捷操作">
          <div class="quick-actions">
            <el-button type="primary" size="large" icon="EditPen" @click="$router.push('/enterprise/report/create')" style="width:100%;margin-bottom:12px">
              新建月度填报
            </el-button>
            <el-button type="success" size="large" icon="List" @click="$router.push('/enterprise/report/list')" style="width:100%">
              查看我的报表
            </el-button>
          </div>
          <el-divider />
          <div class="tips">
            <h4>填报提示</h4>
            <ul>
              <li>每月15日前完成本月数据填报</li>
              <li>1-3月支持半月触发填报模式</li>
              <li>提交前系统自动进行BR规则校验</li>
              <li>退回的报表请及时修正并重新提交</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http'

const recentReports = ref([])
const stats = ref({ total: 0, pending: 0, approved: 0, rejected: 0 })

const statCards = ref([
  { label: '总报表数', value: 0, icon: 'Document', color: '#409eff' },
  { label: '待审核', value: 0, icon: 'Clock', color: '#e6a23c' },
  { label: '已批准', value: 0, icon: 'CircleCheck', color: '#67c23a' },
  { label: '已退回', value: 0, icon: 'CircleClose', color: '#f56c6c' },
])

const statusLabel = (s) => ({
  draft:'草稿', submitted:'已提交', city_review:'市级审核中',
  city_approved:'市级通过', city_rejected:'市级退回',
  province_review:'省级审批中', province_approved:'已批准', province_rejected:'省级退回'
}[s] || s)

const statusType = (s) => ({
  draft:'info', city_review:'warning', province_review:'warning',
  province_approved:'success', city_rejected:'danger', province_rejected:'danger'
}[s] || '')

onMounted(async () => {
  const reports = await http.get('/data/reports')
  recentReports.value = reports.slice(0, 5)
  statCards.value[0].value = reports.length
  statCards.value[1].value = reports.filter(r => ['city_review','province_review'].includes(r.status)).length
  statCards.value[2].value = reports.filter(r => r.status === 'province_approved').length
  statCards.value[3].value = reports.filter(r => ['city_rejected','province_rejected'].includes(r.status)).length
})
</script>

<style scoped>
.stat-card { cursor: default; }
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.tips ul { padding-left: 18px; color: #606266; font-size: 13px; line-height: 2; }
</style>
