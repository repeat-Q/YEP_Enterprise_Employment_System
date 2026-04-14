<template>
  <el-card header="企业管理">
    <div style="margin-bottom:16px">
      <el-button type="primary" icon="Plus" @click="showCreate=true">新建企业</el-button>
    </div>
    <el-table :data="enterprises" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="企业名称" min-width="200" />
      <el-table-column prop="credit_code" label="统一信用代码" width="200" />
      <el-table-column prop="city_code" label="城市" width="100" />
      <el-table-column prop="contact_name" label="联系人" />
      <el-table-column prop="contact_phone" label="联系电话" />
    </el-table>

    <el-dialog v-model="showCreate" title="新建企业" width="600px">
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
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createEnterprise">创建</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'

const enterprises = ref([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
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

onMounted(() => {
  loadEnterprises()
})

const createEnterprise = async () => {
  creating.value = true
  try {
    await http.post('/admin/enterprises', form.value)
    ElMessage.success('企业创建成功')
    showCreate.value = false
    loadEnterprises()
  } catch (e) {
    console.error('创建企业失败:', e)
    ElMessage.error('创建企业失败')
  } finally {
    creating.value = false
  }
}
</script>
