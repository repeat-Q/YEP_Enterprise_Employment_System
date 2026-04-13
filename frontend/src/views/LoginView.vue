<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-header">
        <img src="/logo.svg" class="logo" onerror="this.style.display='none'" />
        <h1>云南省企业就业失业数据采集系统</h1>
        <p class="subtitle">Yunnan Enterprise Employment Data Collection System</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large"
            prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="test-accounts">
        <el-collapse>
          <el-collapse-item title="测试账号（点击展开）" name="1">
            <div class="account-list">
              <div v-for="acc in testAccounts" :key="acc.username" class="account-item"
                @click="fillAccount(acc)">
                <span class="role-tag" :class="acc.type">{{ acc.label }}</span>
                <span>{{ acc.username }} / {{ acc.pwd }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const testAccounts = [
  { username: 'enterprise1', pwd: 'ent123456', label: '企业端', type: 'enterprise' },
  { username: 'city_km', pwd: 'city123456', label: '市级审核', type: 'city' },
  { username: 'province', pwd: 'prov123456', label: '省级审批', type: 'province' },
  { username: 'analyst', pwd: 'analyst123', label: '数据分析', type: 'analyst' },
  { username: 'admin', pwd: 'admin123', label: '系统管理员', type: 'admin' },
]

const fillAccount = (acc) => {
  form.value.username = acc.username
  form.value.password = acc.pwd
}

const handleLogin = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await auth.login(form.value.username, form.value.password)
      ElMessage.success(`欢迎回来，${res.real_name}`)
      const redirectMap = {
        enterprise: '/enterprise/dashboard',
        city: '/city/dashboard',
        province: '/province/dashboard',
        province_analyst: '/province/analytics',
        admin: '/province/admin/users'
      }
      router.push(redirectMap[res.role] || '/login')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a3a6e 0%, #0d5c8a 50%, #1a7a4a 100%);
  display: flex; align-items: center; justify-content: center;
}
.login-box {
  background: white; border-radius: 12px; padding: 40px;
  width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-header { text-align: center; margin-bottom: 30px; }
.logo { width: 64px; height: 64px; margin-bottom: 12px; }
h1 { font-size: 20px; color: #1a3a6e; font-weight: 700; margin: 8px 0 4px; }
.subtitle { font-size: 12px; color: #999; }
.login-btn { width: 100%; }
.test-accounts { margin-top: 20px; }
.account-list { display: flex; flex-direction: column; gap: 8px; }
.account-item { display: flex; align-items: center; gap: 10px; padding: 6px 10px;
  border-radius: 6px; cursor: pointer; transition: background 0.2s; }
.account-item:hover { background: #f0f7ff; }
.role-tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; color: white; white-space: nowrap; }
.role-tag.enterprise { background: #409eff; }
.role-tag.city { background: #67c23a; }
.role-tag.province { background: #e6a23c; }
.role-tag.analyst { background: #909399; }
.role-tag.admin { background: #f56c6c; }
</style>
