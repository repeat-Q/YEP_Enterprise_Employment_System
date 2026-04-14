<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>审批管理</span>
        <el-radio-group v-model="statusFilter" @change="loadReports" size="small">
          <el-radio-button value="">全部待审批</el-radio-button>
          <el-radio-button value="province_review">待省级审批</el-radio-button>
          <el-radio-button value="city_review">待市级审核</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <el-table :data="reports" stripe v-loading="loading">
      <el-table-column label="企业名称" min-width="180">
        <template #default="{row}">{{ row.enterprise_name || '企业'+row.enterprise_id }}</template>
      </el-table-column>
      <el-table-column label="报告年月" width="120">
        <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
      </el-table-column>
      <el-table-column prop="current_employed" label="在职人数" width="100" />
      <el-table-column prop="unemployed_count" label="失业人数" width="100" />
      <el-table-column prop="new_employed" label="新增就业" width="100" />
      <el-table-column label="状态" width="120" align="center">
        <template #default="{row}">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="170">
        <template #default="{row}">{{ (row.submit_time||'').slice(0,16).replace('T',' ') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button v-if="row.status === 'province_review'" type="primary" size="small" @click="$router.push('/province/approve/'+row.id)">审批</el-button>
          <el-button v-else-if="row.status === 'city_review'" type="warning" size="small" @click="$router.push('/province/approve/'+row.id)">审核</el-button>
          <el-button v-else size="small" @click="$router.push('/province/approve/'+row.id)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http'

const reports = ref([])
const loading = ref(false)
const statusFilter = ref('')

const statusLabel = (s) => ({
  draft: '草稿', city_review: '待市级审核', city_approved: '市级已通过',
  city_rejected: '市级已驳回', province_review: '待省级审批',
  province_approved: '省级已批准', province_rejected: '省级已驳回'
}[s] || s)

const statusType = (s) => ({
  draft: 'info', city_review: 'warning', city_approved: '',
  city_rejected: 'danger', province_review: '',
  province_approved: 'success', province_rejected: 'danger'
}[s] || 'info')

async function loadReports() {
  loading.value = true
  try {
    if (statusFilter.value) {
      reports.value = await http.get(`/data/province/reports?status_filter=${statusFilter.value}`)
    } else {
      // 获取所有待审批的（市级审核中 + 省级审批中）
      const [cityReports, provinceReports] = await Promise.all([
        http.get('/data/province/reports?status_filter=city_review').catch(() => []),
        http.get('/data/province/reports?status_filter=province_review').catch(() => [])
      ])
      const city = Array.isArray(cityReports) ? cityReports : []
      const province = Array.isArray(provinceReports) ? provinceReports : []
      reports.value = [...province, ...city]
    }
  } catch (e) {
    console.error('加载报表失败:', e)
  } finally { loading.value = false }
}

onMounted(() => { loadReports() })
</script>
