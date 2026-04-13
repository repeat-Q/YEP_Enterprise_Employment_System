<template>
  <div class="report-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报表管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新建报表
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="企业">
          <el-select v-model="searchForm.enterpriseId" placeholder="全部企业" clearable style="width:200px">
            <el-option v-for="e in enterprises" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width:150px">
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="市级审核通过" value="city_approved" />
            <el-option label="省级审批通过" value="province_approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="季度">
          <el-select v-model="searchForm.quarter" placeholder="全部季度" clearable style="width:120px">
            <el-option v-for="q in quarters" :key="q" :label="q" :value="q" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReports">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 报表列表 -->
      <el-table :data="reports" v-loading="loading" stripe>
        <el-table-column prop="enterprise_name" label="企业名称" min-width="180" />
        <el-table-column prop="report_period" label="报表周期" width="120" />
        <el-table-column prop="quarter" label="季度" width="80" align="center" />
        <el-table-column label="就业人数" width="100" align="center">
          <template #default="{ row }">{{ row.employment_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="失业人数" width="100" align="center">
          <template #default="{ row }">{{ row.unemployment_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="失业率" width="80" align="center">
          <template #default="{ row }">
            {{ row.employment_count ? ((row.unemployment_count / row.employment_count) * 100).toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ row.submitted_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button v-if="row.status === 'draft'" size="small" type="primary" @click="editReport(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" size="small" type="success" @click="submitReport(row)">提交</el-button>
            <el-button v-if="['submitted', 'city_approved'].includes(row.status)" size="small" type="warning" @click="rejectReport(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadReports"
        @current-change="loadReports"
        style="margin-top: 16px"
      />
    </el-card>

    <!-- 新建/编辑报表对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingReport ? '编辑报表' : '新建报表'" width="600px" @closed="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="企业" prop="enterprise_id">
          <el-select v-model="form.enterprise_id" placeholder="请选择企业" style="width: 100%">
            <el-option v-for="e in enterprises" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表周期" prop="report_period">
          <el-date-picker v-model="form.report_period" type="month" placeholder="选择月份" value-format="YYYY-MM" style="width: 100%" />
        </el-form-item>
        <el-form-item label="季度" prop="quarter">
          <el-select v-model="form.quarter" placeholder="请选择季度" style="width: 100%">
            <el-option v-for="q in ['Q1','Q2','Q3','Q4']" :key="q" :label="q" :value="q" />
          </el-select>
        </el-form-item>
        <el-form-item label="城镇新增就业人数" prop="urban_employment">
          <el-input-number v-model="form.urban_employment" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="城镇失业人数" prop="urban_unemployment">
          <el-input-number v-model="form.urban_unemployment" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="就业困难人数" prop="employment_difficulty">
          <el-input-number v-model="form.employment_difficulty" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="登记失业人数" prop="registered_unemployment">
          <el-input-number v-model="form.registered_unemployment" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveReport" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="报表详情" width="700px">
      <el-descriptions :column="2" border v-if="currentReport">
        <el-descriptions-item label="企业名称">{{ currentReport.enterprise_name }}</el-descriptions-item>
        <el-descriptions-item label="报表周期">{{ currentReport.report_period }}</el-descriptions-item>
        <el-descriptions-item label="季度">{{ currentReport.quarter }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(currentReport.status)">{{ statusLabel(currentReport.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="城镇新增就业">{{ currentReport.employment_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="城镇失业">{{ currentReport.unemployment_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="就业困难">{{ currentReport.employment_difficulty_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="登记失业">{{ currentReport.registered_unemployment_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="提交时间" :span="2">{{ currentReport.submitted_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentReport.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '@/utils/http'

const loading = ref(false)
const saving = ref(false)
const reports = ref([])
const enterprises = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingReport = ref(null)
const currentReport = ref(null)
const formRef = ref()

const searchForm = reactive({ enterpriseId: null, status: null, quarter: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const quarters = ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4', '2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4', '2026-Q1', '2026-Q2']

const form = reactive({
  enterprise_id: null,
  report_period: '',
  quarter: '',
  urban_employment: 0,
  urban_unemployment: 0,
  employment_difficulty: 0,
  registered_unemployment: 0,
  remark: ''
})

const rules = {
  enterprise_id: [{ required: true, message: '请选择企业', trigger: 'change' }],
  report_period: [{ required: true, message: '请选择报表周期', trigger: 'change' }],
  quarter: [{ required: true, message: '请选择季度', trigger: 'change' }]
}

const statusLabel = (s) => ({ draft: '草稿', submitted: '已提交', city_approved: '市级审核通过', province_approved: '省级审批通过', rejected: '已驳回' }[s] || s)
const statusType = (s) => ({ draft: 'info', submitted: 'warning', city_approved: 'success', province_approved: 'success', rejected: 'danger' }[s] || 'info')

onMounted(() => {
  loadEnterprises()
  loadReports()
})

async function loadEnterprises() {
  try {
    const { data } = await http.get('/api/v1/enterprises/', { params: { page: 1, page_size: 100 } })
    enterprises.value = data.items || data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadReports() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (searchForm.enterpriseId) params.enterprise_id = searchForm.enterpriseId
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.quarter) params.quarter = searchForm.quarter
    const { data } = await http.get('/api/v1/reports/', { params })
    reports.value = data.items || data || []
    pagination.total = data.total || reports.value.length
  } catch (e) {
    ElMessage.error('加载报表列表失败')
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  searchForm.enterpriseId = null
  searchForm.status = null
  searchForm.quarter = null
  pagination.page = 1
  loadReports()
}

function resetForm() {
  editingReport.value = null
  Object.assign(form, { enterprise_id: null, report_period: '', quarter: '', urban_employment: 0, urban_unemployment: 0, employment_difficulty: 0, registered_unemployment: 0, remark: '' })
}

function editReport(row) {
  editingReport.value = row
  Object.assign(form, {
    enterprise_id: row.enterprise_id,
    report_period: row.report_period,
    quarter: row.quarter,
    urban_employment: row.urban_employment || 0,
    urban_unemployment: row.urban_unemployment || 0,
    employment_difficulty: row.employment_difficulty || 0,
    registered_unemployment: row.registered_unemployment || 0,
    remark: row.remark || ''
  })
  showCreateDialog.value = true
}

async function saveReport() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = { ...form, employment_count: form.urban_employment, unemployment_count: form.urban_unemployment, employment_difficulty_count: form.employment_difficulty, registered_unemployment_count: form.registered_unemployment }
      if (editingReport.value) {
        await http.put(`/api/v1/reports/${editingReport.value.id}`, payload)
        ElMessage.success('报表更新成功')
      } else {
        await http.post('/api/v1/reports/', payload)
        ElMessage.success('报表创建成功')
      }
      showCreateDialog.value = false
      loadReports()
    } catch (e) {
      ElMessage.error(editingReport.value ? '更新失败' : '创建失败')
    } finally {
      saving.value = false
    }
  })
}

async function submitReport(row) {
  try {
    await ElMessageBox.confirm('确定要提交此报表吗？提交后将进入审核流程。', '提交确认', { type: 'warning' })
    await http.put(`/api/v1/reports/${row.id}/submit`)
    ElMessage.success('提交成功')
    loadReports()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('提交失败')
  }
}

async function rejectReport(row) {
  try {
    await ElMessageBox.prompt('请输入驳回原因', '驳回报表', { type: 'warning', confirmButtonText: '确定驳回', cancelButtonText: '取消' })
      .then(async ({ value }) => {
        await http.put(`/api/v1/reports/${row.id}/reject`, { reason: value })
        ElMessage.success('已驳回')
        loadReports()
      })
  } catch (e) {
    if (e !== 'cancel') {}
  }
}

function viewDetail(row) {
  currentReport.value = row
  showDetailDialog.value = true
}
</script>

<style scoped>
.report-manage { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 16px; }
</style>
