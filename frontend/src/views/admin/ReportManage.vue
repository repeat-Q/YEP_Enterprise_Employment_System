<template>
  <div class="report-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报表管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建报表
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="企业">
          <el-select v-model="searchForm.enterprise_id" placeholder="全部企业" clearable style="width:200px">
            <el-option v-for="e in enterprises" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width:150px">
            <el-option label="草稿" value="draft" />
            <el-option label="市级审核中" value="city_review" />
            <el-option label="市级已通过" value="city_approved" />
            <el-option label="省级审批中" value="province_review" />
            <el-option label="省级已批准" value="province_approved" />
            <el-option label="市级已驳回" value="city_rejected" />
            <el-option label="省级已驳回" value="province_rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReports">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 报表列表 -->
      <el-table :data="reports" v-loading="loading" stripe border>
        <el-table-column prop="enterprise_name" label="企业名称" min-width="180" />
        <el-table-column prop="report_period" label="报表周期" width="120" />
        <el-table-column prop="quarter" label="季度" width="80" align="center" />
        <el-table-column label="当期在职" width="100" align="center">
          <template #default="{ row }">{{ row.current_employed || 0 }}</template>
        </el-table-column>
        <el-table-column label="失业人数" width="100" align="center">
          <template #default="{ row }">{{ row.unemployed_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="新增就业" width="100" align="center">
          <template #default="{ row }">{{ row.new_employed || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button v-if="row.status === 'draft'" size="small" type="primary" @click="editReport(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" size="small" type="success" @click="submitReport(row)">提交</el-button>
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
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="企业" prop="enterprise_id">
          <el-select v-model="form.enterprise_id" placeholder="请选择企业" style="width: 100%">
            <el-option v-for="e in enterprises" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表月份" prop="report_period">
          <el-date-picker v-model="form.report_period" type="month" placeholder="选择月份" value-format="YYYY-MM" style="width: 100%" />
        </el-form-item>
        <el-form-item label="当期在职人数" prop="current_employed">
          <el-input-number v-model="form.current_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="失业人数" prop="unemployed_count">
          <el-input-number v-model="form.unemployed_count" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="新增就业人数">
          <el-input-number v-model="form.new_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="减少就业人数">
          <el-input-number v-model="form.lost_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="残疾人就业">
          <el-input-number v-model="form.disabled_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="退役军人就业">
          <el-input-number v-model="form.veteran_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="毕业生就业">
          <el-input-number v-model="form.graduate_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="脱贫人口就业">
          <el-input-number v-model="form.poverty_employed" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="平均工资(元/月)">
          <el-input-number v-model="form.avg_salary" :min="0" style="width: 100%" />
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
        <el-descriptions-item label="当期在职">{{ currentReport.current_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="失业人数">{{ currentReport.unemployed_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="新增就业">{{ currentReport.new_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="减少就业">{{ currentReport.lost_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="残疾人就业">{{ currentReport.disabled_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="退役军人就业">{{ currentReport.veteran_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="毕业生就业">{{ currentReport.graduate_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="脱贫人口就业">{{ currentReport.poverty_employed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="平均工资">{{ currentReport.avg_salary || 0 }} 元/月</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ currentReport.submitted_at || '-' }}</el-descriptions-item>
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

const searchForm = reactive({ enterprise_id: null, status: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const form = reactive({
  enterprise_id: null,
  report_period: '',
  current_employed: 0,
  unemployed_count: 0,
  new_employed: 0,
  lost_employed: 0,
  disabled_employed: 0,
  veteran_employed: 0,
  graduate_employed: 0,
  poverty_employed: 0,
  avg_salary: 0,
  remark: ''
})

const rules = {
  enterprise_id: [{ required: true, message: '请选择企业', trigger: 'change' }],
  report_period: [{ required: true, message: '请选择报表月份', trigger: 'change' }]
}

const statusLabel = (s) => ({
  draft: '草稿',
  submitted: '已提交',
  city_review: '市级审核中',
  city_approved: '市级已通过',
  city_rejected: '市级已驳回',
  province_review: '省级审批中',
  province_approved: '省级已批准',
  province_rejected: '省级已驳回'
}[s] || s)

const statusType = (s) => ({
  draft: 'info',
  submitted: 'warning',
  city_review: '',
  city_approved: 'success',
  city_rejected: 'danger',
  province_review: '',
  province_approved: 'success',
  province_rejected: 'danger'
}[s] || 'info')

onMounted(() => {
  loadEnterprises()
  loadReports()
})

async function loadEnterprises() {
  try {
    const res = await http.get('/admin/enterprises')
    enterprises.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.error('加载企业列表失败:', e)
  }
}

async function loadReports() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (searchForm.enterprise_id) params.enterprise_id = searchForm.enterprise_id
    if (searchForm.status) params.status = searchForm.status
    
    const res = await http.get('/admin/reports', { params })
    reports.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载报表列表失败:', e)
    ElMessage.error('加载报表列表失败')
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  searchForm.enterprise_id = null
  searchForm.status = null
  pagination.page = 1
  loadReports()
}

function openCreateDialog() {
  editingReport.value = null
  Object.assign(form, {
    enterprise_id: null, report_period: '',
    current_employed: 0, unemployed_count: 0,
    new_employed: 0, lost_employed: 0,
    disabled_employed: 0, veteran_employed: 0,
    graduate_employed: 0, poverty_employed: 0,
    avg_salary: 0, remark: ''
  })
  showCreateDialog.value = true
}

function resetForm() {
  editingReport.value = null
}

function editReport(row) {
  editingReport.value = row
  const period = `${row.report_year}-${String(row.report_month).padStart(2, '0')}`
  Object.assign(form, {
    enterprise_id: row.enterprise_id,
    report_period: period,
    current_employed: row.current_employed || 0,
    unemployed_count: row.unemployed_count || 0,
    new_employed: row.new_employed || 0,
    lost_employed: row.lost_employed || 0,
    disabled_employed: row.disabled_employed || 0,
    veteran_employed: row.veteran_employed || 0,
    graduate_employed: row.graduate_employed || 0,
    poverty_employed: row.poverty_employed || 0,
    avg_salary: row.avg_salary || 0,
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
      const payload = { ...form }
      if (editingReport.value) {
        await http.put(`/admin/reports/${editingReport.value.id}`, payload)
        ElMessage.success('报表更新成功')
      } else {
        await http.post('/admin/reports', payload)
        ElMessage.success('报表创建成功')
      }
      showCreateDialog.value = false
      loadReports()
    } catch (e) {
      console.error('保存报表失败:', e)
      ElMessage.error(editingReport.value ? '更新失败' : '创建失败')
    } finally {
      saving.value = false
    }
  })
}

async function submitReport(row) {
  try {
    await ElMessageBox.confirm('确定要提交此报表吗？提交后将进入审核流程。', '提交确认', { type: 'warning' })
    await http.put(`/admin/reports/${row.id}/submit`)
    ElMessage.success('提交成功')
    loadReports()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('提交失败')
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
