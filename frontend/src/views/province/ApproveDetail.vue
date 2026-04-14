<template>
  <el-card v-loading="loading">
    <template #header>
      <div style="display:flex;align-items:center;gap:12px">
        <el-button link icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <span>{{ isCityReview ? '市级审核' : '省级审批' }} — 报表 #{{ report?.id }}</span>
        <el-tag v-if="report" :type="statusType(report.status)">{{ statusLabel(report.status) }}</el-tag>
      </div>
    </template>
    <template v-if="report">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="企业ID">{{ report.enterprise_id }}</el-descriptions-item>
        <el-descriptions-item label="报告年月">{{ report.report_year }}年{{ report.report_month }}月</el-descriptions-item>
        <el-descriptions-item label="当期在职">{{ report.current_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="建档期基准">{{ report.baseline_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="新增就业">{{ report.new_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="减少就业">{{ report.lost_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="失业人数">{{ report.unemployed_count || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="再就业">{{ report.reemployed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="残疾人就业">{{ report.disabled_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="退役军人">{{ report.veteran_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="应届毕业生">{{ report.graduate_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="脱贫人口">{{ report.poverty_employed || 0 }} 人</el-descriptions-item>
        <el-descriptions-item label="平均工资">{{ report.avg_salary || 0 }} 元/月</el-descriptions-item>
        <el-descriptions-item label="工资总额">{{ report.total_salary || 0 }} 万元</el-descriptions-item>
        <el-descriptions-item label="备注">{{ report.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-alert v-if="report.city_review_comment" type="info" style="margin-top:12px"
        :title="'市级审核意见：'+report.city_review_comment" :closable="false" />
      <el-divider />
      <el-form label-width="100px" style="max-width:500px" v-if="canApprove">
        <el-form-item :label="isCityReview ? '审核意见' : '审批意见'">
          <el-input type="textarea" v-model="comment" :rows="3" placeholder="请填写审批意见" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="submitting" @click="doApprove(true)">{{ isCityReview ? '通过（提交省级）' : '批准' }}</el-button>
          <el-button type="danger" :loading="submitting" @click="doApprove(false)">退回</el-button>
        </el-form-item>
      </el-form>
      <el-alert v-else type="info" :closable="false" style="margin-top:12px">
        <template #title>该报表当前状态为「{{ statusLabel(report.status) }}」，无需审批操作</template>
      </el-alert>
    </template>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'

const route = useRoute(); const router = useRouter()
const report = ref(null); const loading = ref(false)
const submitting = ref(false); const comment = ref('')

const isCityReview = computed(() => report.value?.status === 'city_review')
const canApprove = computed(() => report.value?.status === 'city_review' || report.value?.status === 'province_review')

const statusLabel = (s) => ({
  draft: '草稿', city_review: '待市级审核', city_approved: '市级已通过',
  city_rejected: '市级已驳回', province_review: '待省级审批',
  province_approved: '省级已批准', province_rejected: '省级已驳回'
}[s] || s)

const statusType = (s) => ({
  draft: 'info', city_review: 'warning', city_approved: '',
  city_rejected: 'danger', province_review: '',
  province_approved: 'success', province_rejected: 'danger'
}[s] || 'info')

onMounted(async () => {
  loading.value = true
  try { report.value = await http.get(`/data/reports/${route.params.id}`) }
  catch (e) { ElMessage.error('加载报表失败') }
  finally { loading.value = false }
})

const doApprove = async (approve) => {
  submitting.value = true
  try {
    if (isCityReview.value) {
      // 市级审核（管理员代为审核）
      await http.post(`/data/city/reports/${route.params.id}/review`, { approve, comment: comment.value })
      ElMessage.success(approve ? '市级审核通过，已提交省级' : '已退回企业')
    } else {
      // 省级审批
      await http.post(`/data/province/reports/${route.params.id}/approve`, { approve, comment: comment.value })
      ElMessage.success(approve ? '已批准，数据归档' : '已退回市级')
    }
    router.push('/province/approve')
  } catch (e) {
    ElMessage.error('操作失败')
  } finally { submitting.value = false }
}
</script>
