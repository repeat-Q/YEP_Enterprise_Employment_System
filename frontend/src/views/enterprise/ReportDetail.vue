<template>
  <el-card v-loading="loading">
    <template #header>
      <div style="display:flex;align-items:center;gap:12px">
        <el-button link icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <span>报表详情 #{{ report?.id }}</span>
        <el-tag :type="statusType(report?.status)">{{ statusLabel(report?.status) }}</el-tag>
      </div>
    </template>
    <template v-if="report">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="报告年月">{{ report.report_year }}年{{ report.report_month }}月</el-descriptions-item>
        <el-descriptions-item label="填报类型">{{ report.period_type==='half_monthly'?`半月（${report.half_period===1?'上':'下'}半月）`:'月度' }}</el-descriptions-item>
        <el-descriptions-item label="当前状态"><el-tag :type="statusType(report.status)">{{ statusLabel(report.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="建档期就业基准">{{ report.baseline_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="当期在职人数">{{ report.current_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="新增就业">{{ report.new_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="减少就业">{{ report.lost_employed }} 人</el-descriptions-item>
        <el-descriptions-item label="失业人数">{{ report.unemployed_count }} 人</el-descriptions-item>
        <el-descriptions-item label="再就业人数">{{ report.reemployed }} 人</el-descriptions-item>
        <el-descriptions-item label="平均工资">{{ report.avg_salary }} 元/月</el-descriptions-item>
        <el-descriptions-item label="工资总额">{{ report.total_salary }} 万元</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ report.submit_time?.slice(0,19).replace('T',' ') || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-alert v-if="report.city_review_comment" type="warning" style="margin-top:16px"
        :title="'市级审核意见：' + report.city_review_comment" :closable="false" />
      <el-alert v-if="report.province_review_comment" type="info" style="margin-top:8px"
        :title="'省级审批意见：' + report.province_review_comment" :closable="false" />
    </template>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import http from '@/utils/http'

const route = useRoute()
const report = ref(null)
const loading = ref(false)
const statusLabel = (s) => ({
  draft:'草稿', city_review:'市级审核中', city_rejected:'市级退回',
  province_review:'省级审批中', province_approved:'已批准', province_rejected:'省级退回'
}[s] || s)
const statusType = (s) => ({
  draft:'info', city_review:'warning', province_review:'warning',
  province_approved:'success', city_rejected:'danger', province_rejected:'danger'
}[s] || '')

onMounted(async () => {
  loading.value = true
  try { report.value = await http.get(`/data/reports/${route.params.id}`) }
  finally { loading.value = false }
})
</script>
