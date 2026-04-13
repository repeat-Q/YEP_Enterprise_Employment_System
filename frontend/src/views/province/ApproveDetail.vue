<template>
  <el-card v-loading="loading">
    <template #header>
      <div style="display:flex;align-items:center;gap:12px">
        <el-button link icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <span>省级审批 — 报表 #{{ report?.id }}</span>
      </div>
    </template>
    <template v-if="report">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="企业ID">{{ report.enterprise_id }}</el-descriptions-item>
        <el-descriptions-item label="报告年月">{{ report.report_year }}年{{ report.report_month }}月</el-descriptions-item>
        <el-descriptions-item label="当期在职">{{ report.current_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="建档期基准">{{ report.baseline_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="新增就业">{{ report.new_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="减少就业">{{ report.lost_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="失业人数">{{ report.unemployed_count }} 人</el-descriptions-item>
        <el-descriptions-item label="再就业">{{ report.reemployed }} 人</el-descriptions-item>
        <el-descriptions-item label="残疾人就业">{{ report.disabled_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="退役军人">{{ report.veteran_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="应届毕业生">{{ report.graduate_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="脱贫人口">{{ report.poverty_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="平均工资">{{ report.avg_salary }} 元/月</el-descriptions-item>
        <el-descriptions-item label="工资总额">{{ report.total_salary }} 万元</el-descriptions-item>
      </el-descriptions>
      <el-alert v-if="report.city_review_comment" type="info" style="margin-top:12px"
        :title="'市级意见：'+report.city_review_comment" :closable="false" />
      <el-divider />
      <el-form label-width="100px" style="max-width:500px">
        <el-form-item label="审批意见">
          <el-input type="textarea" v-model="comment" :rows="3" placeholder="请填写审批意见" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="submitting" @click="doApprove(true)">批准</el-button>
          <el-button type="danger" :loading="submitting" @click="doApprove(false)">退回</el-button>
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

const route = useRoute(); const router = useRouter()
const report = ref(null); const loading = ref(false)
const submitting = ref(false); const comment = ref('')

onMounted(async () => {
  loading.value = true
  try { report.value = await http.get(`/data/reports/${route.params.id}`) }
  finally { loading.value = false }
})

const doApprove = async (approve) => {
  submitting.value = true
  try {
    await http.post(`/data/province/reports/${route.params.id}/approve`, { approve, comment: comment.value })
    ElMessage.success(approve ? '已批准，数据归档' : '已退回市级')
    router.push('/province/approve')
  } finally { submitting.value = false }
}
</script>
