<template>
  <el-card header="企业管理">
    <div style="margin-bottom:16px">
      <el-button type="primary" icon="Plus" @click="openCreate">新建企业</el-button>
    </div>
    <el-table :data="enterprises" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="企业名称" min-width="180" />
      <el-table-column prop="credit_code" label="统一信用代码" width="200" />
      <el-table-column prop="city_code" label="城市" width="100" />
      <el-table-column prop="contact_name" label="联系人" width="100" />
      <el-table-column prop="contact_phone" label="联系电话" width="130" />
      <el-table-column label="状态" width="80" align="center">
        <template #default="{row}">
          <el-tag :type="row.is_active?'success':'danger'">{{ row.is_active?'正常':'停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{row}">
          <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteEnterprise(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑企业' : '新建企业'" width="600px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="企业名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="统一信用代码"><el-input v-model="form.credit_code" /></el-form-item>
        <el-form-item label="城市代码"><el-input v-model="form.city_code" placeholder="如530100" /></el-form-item>
        <el-form-item label="区县代码"><el-input v-model="form.district_code" /></el-form-item>
        <el-form-item label="行业代码"><el-input v-model="form.industry_code" /></el-form-item>
        <el-form-item label="企业类型"><el-input v-model="form.enterprise_type" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_name" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.contact_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEnterprise">{{ editingId ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '@/utils/http'

const enterprises = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const form = ref({ name:'', credit_code:'', city_code:'', district_code:'', industry_code:'', enterprise_type:'', address:'', contact_name:'', contact_phone:'' })

async function loadEnterprises() {
  loading.value = true
  try {
    const res = await http.get('/admin/enterprises')
    enterprises.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.error('加载企业列表失败:', e)
    ElMessage.error('加载企业列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadEnterprises() })

function openCreate() {
  editingId.value = null
  form.value = { name:'', credit_code:'', city_code:'', district_code:'', industry_code:'', enterprise_type:'', address:'', contact_name:'', contact_phone:'' }
  showDialog.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = { 
    name: row.name || '', credit_code: row.credit_code || '', 
    city_code: row.city_code || '', district_code: row.district_code || '',
    industry_code: row.industry_code || '', enterprise_type: row.enterprise_type || '',
    address: row.address || '', contact_name: row.contact_name || '', 
    contact_phone: row.contact_phone || ''
  }
  showDialog.value = true
}

async function saveEnterprise() {
  saving.value = true
  try {
    if (editingId.value) {
      await http.put(`/admin/enterprises/${editingId.value}`, form.value)
      ElMessage.success('企业更新成功')
    } else {
      await http.post('/admin/enterprises', form.value)
      ElMessage.success('企业创建成功')
    }
    showDialog.value = false
    loadEnterprises()
  } catch (e) {
    console.error('保存企业失败:', e)
    ElMessage.error(editingId.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

async function deleteEnterprise(row) {
  try {
    await ElMessageBox.confirm(`确定要删除企业"${row.name}"吗？`, '删除确认', { type: 'warning' })
    await http.delete(`/admin/enterprises/${row.id}`)
    ElMessage.success('企业已删除')
    loadEnterprises()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除企业失败:', e)
      ElMessage.error('删除失败')
    }
  }
}
</script>
