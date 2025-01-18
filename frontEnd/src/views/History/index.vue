<template>
    <div class="history-container">
        <el-card class="history-card">
            <template #header>
                <div class="card-header">
                    <span>会议历史记录</span>
                </div>
            </template>

            <el-table :data="history" style="width: 100%" border stripe>
                <el-table-column prop="summaryText" label="会议总结" width="300" />
                <el-table-column prop="blinkCount" label="眨眼次数" width="120" />
                <el-table-column prop="mouthOpenCount" label="张嘴次数" width="120" />
                <el-table-column prop="blinkTimes" label="眨眼时间" width="200">
                    <template #default="{ row }">
                        <div>{{ row.blinkTimes.join(', ') }} 秒</div>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="200" style="justify-content: center">
                    <template #default="{ row }">
                        <el-button style="margin-left: 30px" type="primary" @click="exportPdf(row, 'zh')">导出中文文档</el-button>
                        <el-button style="margin: 20px 30px" type="primary" @click="exportPdf(row, 'en')">导出英文文档</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { ElLoading } from 'element-plus'; // 引入 Loading 组件

interface Record {
    index: number;
    speaker: string;
    content: string;
    currentTime: string;
    meetingDuration: number;
}

interface HistoryItem {
    id: string; // 新增字段：记录的唯一标识
    records: Record[];
    summaryText: string;
    blinkCount: number;
    mouthOpenCount: number;
    blinkTimes: number[];
}

interface SearchResult {
    id: string; // 新增字段：记录的唯一标识
    records: Record[];
    summaryText: string;
    blinkCount: number;
    mouthOpenCount: number;
    blinkTimes: number[];
}

const history = ref<HistoryItem[]>([]);

// 获取历史记录
const fetchHistory = async () => {
    try {
        const response = await axios.get('http://192.168.1.17:8000/get-history');
        // 将 _id 映射到 id
        history.value = response.data.history.map((item: any) => ({
            ...item,
            id: item._id, // 将 _id 映射到 id
        }));
        console.log(history.value);
    } catch (error) {
        console.error('获取历史记录失败:', error);
    }
};

// 导出 PDF 文档
const exportPdf = async (row: HistoryItem | SearchResult, language: string) => {
    let loadingInstance: any = null; // 用于保存 Loading 实例

    try {
        // 如果是英文文档，显示加载动画
        if (language === 'en') {
            loadingInstance = ElLoading.service({
                lock: true,
                text: '正在生成英文文档...',
                background: 'rgba(0, 0, 0, 0.7)',
            });
        }

        console.log('row.id',row.id)
        const endpoint = language === 'zh' ? '/generate-pdf-zh' : '/generate-pdf-en';
        const response = await axios.post(`http://192.168.1.17:8000${endpoint}`, {
            _id: row.id, // 确保传递 id 字段
            records: row.records,
            summaryText: row.summaryText,
            blinkCount: row.blinkCount,
            mouthOpenCount: row.mouthOpenCount,
            blinkTimes: row.blinkTimes,
        }, {
            responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `report_${language}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        ElMessage.error('导出失败');
        console.error('导出失败:', error);
    } finally {
        // 关闭加载动画
        if (loadingInstance) {
            loadingInstance.close();
        }
    }
};

onMounted(() => {
    fetchHistory();
});
</script>

<style scoped>
.history-container {
    padding: 20px;
}

.history-card {
    max-width: 1200px;
    margin: 0 auto;
}

.card-header {
    font-size: 18px;
    font-weight: bold;
}
</style>