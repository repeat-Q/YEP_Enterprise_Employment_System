<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>新建就业失业数据填报</span>
          <el-tag type="warning" v-if="isHalfMonthMode">半月触发模式（{{ form.report_month }}月）</el-tag>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="160px" style="max-width:800px">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="报告年份" prop="report_year">
              <el-input-number v-model="form.report_year" :min="2020" :max="2030" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="报告月份" prop="report_month">
              <el-select v-model="form.report_month" style="width:100%" @change="onMonthChange">
                <el-option v-for="m in 12" :key="m" :value="m" :label="m+'月'" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8" v-if="isHalfMonthMode">
            <el-form-item label="调查期" prop="half_period">
              <el-radio-group v-model="form.half_period">
                <el-radio :value="1">上半月（1-15日）</el-radio>
                <el-radio :value="2">下半月（16日起）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 就业数据 -->
        <el-divider content-position="left">就业数据</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="建档期就业基准人数" prop="baseline_employed">
              <el-input-number v-model="form.baseline_employed" :min="0" style="width:100%" />
              <div class="field-tip">BR-01基准值：用于动态减员校验</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当期在职人数" prop="current_employed">
              <el-input-number v-model="form.current_employed" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="新增就业人数" prop="new_employed">
              <el-input-number v-model="form.new_employed" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="减少就业人数" prop="lost_employed">
              <el-input-number v-model="form.lost_employed" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 失业数据 -->
        <el-divider content-position="left">失业数据</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="失业人员数" prop="unemployed_count">
              <el-input-number v-model="form.unemployed_count" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="新增失业人员" prop="new_unemployed">
              <el-input-number v-model="form.new_unemployed" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="再就业人数" prop="reemployed">
              <el-input-number v-model="form.reemployed" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 特殊群体 -->
        <el-divider content-position="left">特殊群体就业</el-divider>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="残疾人就业"><el-input-number v-model="form.disabled_employed" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="退役军人就业"><el-input-number v-model="form.veteran_employed" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="应届毕业生就业"><el-input-number v-model="form.graduate_employed" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="脱贫人口就业"><el-input-number v-model="form.poverty_employed" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>

        <!-- 薪资数据 -->
        <el-divider content-position="left">薪资数据</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="平均工资（元/月）">
              <el-input-number v-model="form.avg_salary" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工资总额（万元）">
              <el-input-number v-model="form.total_salary" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input type="textarea" v-model="form.remark" :rows="3" placeholder="可填写补充说明" />
        </el-form-item>

        <!-- BR校验结果 -->
        <el-alert v-if="brErrors.length" type="error" style="margin-bottom:16px" :closable="false">
          <template #title>BR红线校验未通过，请修正以下数据：</template>
          <ul style="margin:8px 0;padding-left:20px">
            <li v-for="e in brErrors" :key="e.rule"><strong>[{{ e.rule }}]</strong> {{ e.message }}</li>
          </ul>
        </el-alert>

        <el-form-item>
          <el-button @click="saveDraft" :loading="saving">保存草稿</el-button>
          <el-button type="primary" @click="submitReport" :loading="submitting">提交填报</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'

const router = useRouter()
const formRef = ref()
const saving = ref(false)
const submitting = ref(false)
const brErrors = ref([])
const reportId = ref(null)

const now = new Date()
const form = ref({
  report_year: now.getFullYear(),
  report_month: now.getMonth() + 1,
  period_type: 'monthly',
  half_period: null,
  baseline_employed: 0,
  current_employed: 0,
  new_employed: 0,
  lost_employed: 0,
  unemployed_count: 0,
  new_unemployed: 0,
  reemployed: 0,
  disabled_employed: 0,
  veteran_employed: 0,
  graduate_employed: 0,
  poverty_employed: 0,
  avg_salary: 0,
  total_salary: 0,
  remark: ''
})

const isHalfMonthMode = computed(() => [1, 2, 3].includes(form.value.report_month))

const onMonthChange = (month) => {
  if ([1, 2, 3].includes(month)) {
    form.value.period_type = 'half_monthly'
    form.value.half_period = 1
  } else {
    form.value.period_type = 'monthly'
    form.value.half_period = null
  }
}

const rules = {
  report_year: [{ required: true }],
  report_month: [{ required: true }],
}

const saveDraft = async () => {
  saving.value = true
  try {
    if (reportId.value) {
      await http.put(`/data/reports/${reportId.value}`, form.value)
    } else {
      const res = await http.post('/data/reports', form.value)
      reportId.value = res.id
    }
    ElMessage.success('草稿已保存')
  } finally {
    saving.value = false
  }
}

const submitReport = async () => {
  brErrors.value = []
  submitting.value = true
  try {
    // 先保存
    if (!reportId.value) {
      const res = await http.post('/data/reports', form.value)
      reportId.value = res.id
    } else {
      await http.put(`/data/reports/${reportId.value}`, form.value)
    }
    // 提交
    await http.post(`/data/reports/${reportId.value}/submit`)
    ElMessage.success('填报提交成功，等待市级审核')
    router.push('/enterprise/report/list')
  } catch (err) {
    if (err.response?.data?.detail?.br_errors) {
      brErrors.value = err.response.data.detail.br_errors
      ElMessage.error('BR规则校验未通过，请检查数据')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.field-tip { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
