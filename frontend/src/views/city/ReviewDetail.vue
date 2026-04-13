<template>
  <el-card v-loading="loading">
    <template #header>
      <div style="display:flex;align-items:center;gap:12px">
        <el-button link icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <span>市级审核 — 报表 #{{ report?.id }}</span>
      </div>
    </template>
    <template v-if="report">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="企业ID">{{ report.enterprise_id }}</el-descriptions-item>
        <el-descriptions-item label="报告年月">{{ report.report_year }}年{{ report.report_month }}月</el-descriptions-item>
        <el-descriptions-item label="当期在职">{{ report.current_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="新增就业">{{ report.new_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="减少就业">{{ report.lost_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="失业人数">{{ report.unemployed_count }} 人</el-descriptions-item>
        <el-descriptions-item label="平均工资">{{ report.avg_salary }} 元/月</el-descriptions-item>
        <el-descriptions-item label="工资总额">{{ report.total_salary }} 万元</el-descriptions-item>
        <el-descriptions-item label="备注">{{ report.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />
      <el-form label-width="100px" style="max-width:500px">
        <el-form-item label="审核意见">
          <el-input type="textarea" v-model="comment" :rows="3" placeholder="请填写审核意见（退回时必填）" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="submitting" @click="doReview(true)">通过</el-button>
          <el-button type="danger" :loading="submitting" @click="doReview(false)">退回</el-button>
        </el-form-item>
      </el-form>
    </template>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'

const route = useRoute()
const router = useRouter()
const report = ref(null)
const loading = ref(false)
const submitting = ref(false)
const comment = ref('')

onMounted(async () => {
  loading.value = true
  try { report.value = await http.get(`/data/reports/${route.params.id}`) }
  finally { loading.value = false }
})

const doReview = async (approve) => {
  if (!approve && !comment.value.trim()) {
    ElMessage.warning('退回时请填写审核意见')
    return
  }
  submitting.value = true
  try {
    await http.post(`/data/city/reports/${route.params.id}/review`, { approve, comment: comment.value })
    ElMessage.success(approve ? '已通过，报表进入省级审批' : '已退回企业')
    router.push('/city/review')
  } finally { submitting.value = false }
}
</script>
