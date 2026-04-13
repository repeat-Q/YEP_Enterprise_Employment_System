import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('@/views/LoginView.vue') },
    {
      path: '/enterprise',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true, roles: ['enterprise'] },
      children: [
        { path: '', redirect: '/enterprise/dashboard' },
        { path: 'dashboard', component: () => import('@/views/enterprise/Dashboard.vue') },
        { path: 'report/create', component: () => import('@/views/enterprise/ReportCreate.vue') },
        { path: 'report/list', component: () => import('@/views/enterprise/ReportList.vue') },
        { path: 'report/:id', component: () => import('@/views/enterprise/ReportDetail.vue') },
      ]
    },
    {
      path: '/city',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true, roles: ['city'] },
      children: [
        { path: '', redirect: '/city/dashboard' },
        { path: 'dashboard', component: () => import('@/views/city/Dashboard.vue') },
        { path: 'review', component: () => import('@/views/city/ReviewList.vue') },
        { path: 'review/:id', component: () => import('@/views/city/ReviewDetail.vue') },
      ]
    },
    {
      path: '/province',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true, roles: ['province', 'province_analyst', 'admin'] },
      children: [
        { path: '', redirect: '/province/dashboard' },
        { path: 'dashboard', component: () => import('@/views/province/Dashboard.vue') },
        { path: 'approve', component: () => import('@/views/province/ApproveList.vue') },
        { path: 'approve/:id', component: () => import('@/views/province/ApproveDetail.vue') },
        { path: 'analytics', component: () => import('@/views/province/Analytics.vue') },
        { path: 'screen', component: () => import('@/views/province/DataScreen.vue') },
        { path: 'admin/users', component: () => import('@/views/admin/UserManage.vue') },
        { path: 'admin/enterprises', component: () => import('@/views/admin/EnterpriseManage.vue') },
        { path: 'admin/reports', component: () => import('@/views/admin/ReportManage.vue') },
      ]
    },
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (to.meta.requiresAuth && !token) return next('/login')
  if (to.meta.roles && !to.meta.roles.includes(role)) {
    // 根据角色跳转
    const redirectMap = { enterprise: '/enterprise', city: '/city', province: '/province', province_analyst: '/province', admin: '/province' }
    return next(redirectMap[role] || '/login')
  }
  next()
})

export default router
