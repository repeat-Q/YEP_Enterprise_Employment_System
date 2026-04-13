<template>
  <el-card header="省级待审批报表">
    <el-table :data="reports" stripe v-loading="loading">
      <el-table-column prop="enterprise_id" label="企业ID" width="80" />
      <el-table-column label="报告年月" width="120">
        <template #default="{row}">{{ row.report_year }}年{{ row.report_month }}月</template>
      </el-table-column>
      <el-table-column prop="current_employed" label="在职人数" />
      <el-table-column prop="unemployed_count" label="失业人数" />
      <el-table-column prop="new_employed" label="新增就业" />
      <el-table-column label="操作" width="120">
        <template #default="{row}">
          <el-button type="primary" size="small" @click="$router.push('/province/approve/'+row.id)">审批</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http'
const reports = ref([])
const loading = ref(false)
onMounted(async () => {
  loading.value = true
  try { reports.value = await http.get('/data/province/reports') }
  finally { loading.value = false }
})
</script>
