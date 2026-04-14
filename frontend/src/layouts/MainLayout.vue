<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-text">YEP系统</span>
        <span class="logo-sub">就业数据采集</span>
      </div>
      <el-menu :default-active="activeMenu" router background-color="#1a3a6e"
        text-color="#c0d4f0" active-text-color="#ffffff" class="sidebar-menu">
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="info" style="margin-right:12px">{{ roleLabel }}</el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar size="small" :style="{background: '#409eff'}">{{ auth.realName?.charAt(0) }}</el-avatar>
              <span style="margin-left:8px">{{ auth.realName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const activeMenu = computed(() => route.path)
const currentPageTitle = computed(() => route.meta.title || '')

const roleMenus = {
  enterprise: [
    { path: '/enterprise/dashboard', icon: 'House', label: '首页概览' },
    { path: '/enterprise/report/create', icon: 'EditPen', label: '新建填报' },
    { path: '/enterprise/report/list', icon: 'List', label: '我的报表' },
  ],
  city: [
    { path: '/city/dashboard', icon: 'House', label: '首页概览' },
    { path: '/city/review', icon: 'Checked', label: '待审核报表' },
    { path: '/city/analytics', icon: 'TrendCharts', label: '数据分析' },
    { path: '/city/screen', icon: 'Monitor', label: '数据大屏' },
  ],
  province: [
    { path: '/province/dashboard', icon: 'House', label: '首页概览' },
    { path: '/province/admin/reports', icon: 'Document', label: '报表管理' },
    { path: '/province/approve', icon: 'Stamp', label: '待审批报表' },
    { path: '/province/analytics', icon: 'TrendCharts', label: '数据分析' },
    { path: '/province/screen', icon: 'Monitor', label: '数据大屏' },
  ],
  province_analyst: [
    { path: '/province/analytics', icon: 'TrendCharts', label: '数据分析' },
    { path: '/province/screen', icon: 'Monitor', label: '数据大屏' },
  ],
  admin: [
    { path: '/province/dashboard', icon: 'House', label: '首页概览' },
    { path: '/province/admin/reports', icon: 'Document', label: '报表管理' },
    { path: '/province/approve', icon: 'Stamp', label: '审批管理' },
    { path: '/province/analytics', icon: 'TrendCharts', label: '数据分析' },
    { path: '/province/admin/users', icon: 'User', label: '用户管理' },
    { path: '/province/admin/enterprises', icon: 'OfficeBuilding', label: '企业管理' },
  ]
}

const menuItems = computed(() => roleMenus[auth.role] || [])
const roleLabelMap = { enterprise: '企业用户', city: '市级审核', province: '省级审批', province_analyst: '数据分析员', admin: '系统管理员' }
const roleLabel = computed(() => roleLabelMap[auth.role] || auth.role)

const handleCommand = (cmd) => {
  if (cmd === 'logout') { auth.logout(); router.push('/login') }
}
</script>

<style scoped>
.main-layout { height: 100vh; }
.sidebar { background: #1a3a6e; display: flex; flex-direction: column; }
.sidebar-logo { padding: 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.logo-text { color: white; font-size: 18px; font-weight: 700; display: block; }
.logo-sub { color: #c0d4f0; font-size: 12px; }
.sidebar-menu { border-right: none; flex: 1; }
.header { background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
.header-right { display: flex; align-items: center; }
.user-info { display: flex; align-items: center; cursor: pointer; }
.main-content { background: #f5f7fa; padding: 20px; overflow-y: auto; }
</style>
