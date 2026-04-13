import { defineStore } from 'pinia'
import http from '@/utils/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('role') || '',
    userId: localStorage.getItem('userId') || '',
    realName: localStorage.getItem('realName') || '',
    enterpriseId: localStorage.getItem('enterpriseId') || null,
  }),
  actions: {
    async login(username, password) {
      const res = await http.post('/auth/login', { username, password })
      this.token = res.access_token
      this.role = res.role
      this.userId = res.user_id
      this.realName = res.real_name
      this.enterpriseId = res.enterprise_id
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('role', res.role)
      localStorage.setItem('userId', res.user_id)
      localStorage.setItem('realName', res.real_name)
      localStorage.setItem('enterpriseId', res.enterprise_id)
      return res
    },
    logout() {
      this.token = ''; this.role = ''; this.userId = ''
      localStorage.clear()
    }
  }
})
