<template>
  <el-card header="用户管理">
    <div style="margin-bottom:16px">
      <el-button type="primary" icon="Plus" @click="showCreate=true">新建用户</el-button>
    </div>
    <el-table :data="users" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="real_name" label="姓名" />
      <el-table-column prop="role" label="角色">
        <template #default="{row}">
          <el-tag :type="roleType(row.role)">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="city_code" label="城市代码" />
      <el-table-column label="状态">
        <template #default="{row}">
          <el-tag :type="row.is_active?'success':'danger'">{{ row.is_active?'启用':'禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{row}">
          <el-button link :type="row.is_active?'danger':'success'" @click="toggle(row)">
            {{ row.is_active?'禁用':'启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建用户" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width:100%">
            <el-option value="enterprise" label="企业用户" />
            <el-option value="city" label="市级审核" />
            <el-option value="province" label="省级审批" />
            <el-option value="province_analyst" label="数据分析员" />
            <el-option value="admin" label="系统管理员" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市代码" v-if="form.role==='city'">
          <el-input v-model="form.city_code" placeholder="如530100" />
        </el-form-item>
        <el-form-item label="企业ID" v-if="form.role==='enterprise'">
          <el-input-number v-model="form.enterprise_id" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createUser">创建</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'

const users = ref([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const form = ref({ username: '', password: '', real_name: '', role: 'enterprise', city_code: '', enterprise_id: null })

const roleLabel = (r) => ({ enterprise:'企业用户', city:'市级审核', province:'省级审批', province_analyst:'数据分析员', admin:'系统管理员' }[r] || r)
const roleType = (r) => ({ enterprise:'primary', city:'success', province:'warning', province_analyst:'info', admin:'danger' }[r] || '')

onMounted(async () => {
  loading.value = true
  try { users.value = await http.get('/admin/users') }
  finally { loading.value = false }
})

const toggle = async (row) => {
  await http.put(`/admin/users/${row.id}/toggle`)
  row.is_active = !row.is_active
  ElMessage.success(row.is_active ? '已启用' : '已禁用')
}

const createUser = async () => {
  creating.value = true
  try {
    const u = await http.post('/admin/users', form.value)
    users.value.push(u)
    showCreate.value = false
    ElMessage.success('用户创建成功')
  } finally { creating.value = false }
}
</script>
