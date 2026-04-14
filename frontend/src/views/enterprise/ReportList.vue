<template>
  <el-card header="我的报表列表">
    <el-table :data="reports" stripe v-loading="loading">
      <el-table-column prop="report_year" label="年份" width="80" />
      <el-table-column label="月份" width="100">
        <template #default="{row}">
          {{ row.report_month }}月
          <el-tag size="small" type="warning" v-if="row.period_type==='half_monthly'">
            {{ row.half_period===1?'上半月':'下半月' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="current_employed" label="在职人数" />
      <el-table-column prop="unemployed_count" label="失业人数" />
      <el-table-column label="状态">
        <template #default="{row}">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="submit_time" label="提交时间" width="180">
        <template #default="{row}">{{ row.submit_time ? row.submit_time.slice(0,19).replace('T',' ') : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{row}">
          <el-button link type="primary" @click="$router.push('/enterprise/report/'+row.id)">查看</el-button>
          <el-button link type="warning" v-if="canEdit(row.status)" @click="editReport(row)">修改</el-button>
          <el-button link type="danger" v-if="canDelete(row.status)" @click="deleteReport(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:right;margin-top:16px">
      <el-button type="primary" @click="$router.push('/enterprise/report/create')">新建填报</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '@/utils/http'

const router = useRouter()
const reports = ref([])
const loading = ref(false)

const statusLabel = (s) => ({
  draft:'草稿', submitted:'已提交', city_review:'市级审核中',
  city_approved:'市级通过', city_rejected:'市级退回',
  province_review:'省级审批中', province_approved:'已批准', province_rejected:'省级退回'
}[s] || s)

const statusType = (s) => ({
  draft:'info', city_review:'warning', province_review:'warning',
  province_approved:'success', city_rejected:'danger', province_rejected:'danger'
}[s] || '')

const canEdit = (s) => ['draft','city_rejected','province_rejected'].includes(s)
const canDelete = (s) => ['draft','city_rejected','province_rejected'].includes(s)
const editReport = (row) => router.push('/enterprise/report/create?edit='+row.id)

const deleteReport = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除 ${row.report_year}年${row.report_month}月 的报表吗？`, '删除确认', { type: 'warning' })
    await http.delete(`/data/reports/${row.id}`)
    ElMessage.success('报表已删除')
    loadReports()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

async function loadReports() {
  loading.value = true
  try { reports.value = await http.get('/data/reports') }
  finally { loading.value = false }
}

onMounted(() => { loadReports() })
</script>
