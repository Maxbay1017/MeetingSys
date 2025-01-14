<template>
    <div class="search-container">
        <el-card class="search-card">
            <template #header>
                <div class="card-header">
                    <span>会议记录搜索</span>
                </div>
            </template>

            <div class="search-box">
                <el-input v-model="keyword" placeholder="请输入关键词" clearable @keyup.enter="handleSearch" />
                <el-button type="primary" @click="handleSearch">搜索</el-button>
            </div>

            <el-table :data="results" style="width: 100%" border stripe v-if="results.length > 0">
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

            <el-empty v-if="results.length === 0 && keyword" description="未找到相关记录" />
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
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

interface SearchResult {
    records: Record[];
    summaryText: string;
    blinkCount: number;
    mouthOpenCount: number;
    blinkTimes: number[];
}

const keyword = ref('');
const results = ref<SearchResult[]>([]);

// 处理搜索
const handleSearch = async () => {
    if (!keyword.value) {
        results.value = [];
        return;
    }

    try {
        const response = await axios.get('http://192.168.1.8:8000/search', {
            params: { keyword: keyword.value },
        });
        results.value = response.data.results;
    } catch (error) {
        ElMessage.error('搜索失败');
        console.error('搜索失败:', error);
        results.value = [];
    }
};

// 导出 PDF 文档
const exportPdf = async (row: SearchResult | HistoryItem, language: string) => {
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

        const endpoint = language === 'zh' ? '/generate-pdf-zh' : '/generate-pdf-en';
        const response = await axios.post(`http://192.168.1.8:8000${endpoint}`, {
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

// const exportPdf = async (row: SearchResult, language: string) => {
//     try {
//         const endpoint = language === 'zh' ? '/generate-pdf-zh' : '/generate-pdf-en';
//         const response = await axios.post(`http://192.168.1.8:8000${endpoint}`, {
//             records: row.records,
//             summaryText: row.summaryText,
//             blinkCount: row.blinkCount,
//             mouthOpenCount: row.mouthOpenCount,
//             blinkTimes: row.blinkTimes,
//         }, {
//             responseType: 'blob',
//         });
//
//         const url = window.URL.createObjectURL(new Blob([response.data]));
//         const link = document.createElement('a');
//         link.href = url;
//         link.setAttribute('download', `report_${language}.pdf`);
//         document.body.appendChild(link);
//         link.click();
//         document.body.removeChild(link);
//     } catch (error) {
//         ElMessage.error('导出失败');
//         console.error('导出失败:', error);
//     }
// };
</script>

<style scoped>
.search-container {
    padding: 20px;
}

.search-card {
    max-width: 1200px;
    margin: 0 auto;
}

.card-header {
    font-size: 18px;
    font-weight: bold;
}

.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
</style>
<!--<template>-->
<!--    <div class="search-container">-->
<!--        <el-card class="search-card">-->
<!--            <template #header>-->
<!--                <div class="card-header">-->
<!--                    <span>会议记录搜索</span>-->
<!--                </div>-->
<!--            </template>-->

<!--            <div class="search-box">-->
<!--                <el-input v-model="keyword" placeholder="请输入关键词" clearable @keyup.enter="handleSearch" />-->
<!--                <el-button type="primary" @click="handleSearch">搜索</el-button>-->
<!--            </div>-->

<!--            <el-table :data="results" style="width: 100%" border stripe v-if="results.length > 0">-->
<!--                <el-table-column prop="summaryText" label="会议总结" width="300" />-->
<!--                <el-table-column prop="blinkCount" label="眨眼次数" width="120" />-->
<!--                <el-table-column prop="mouthOpenCount" label="张嘴次数" width="120" />-->
<!--                <el-table-column prop="blinkTimes" label="眨眼时间" width="200">-->
<!--                    <template #default="{ row }">-->
<!--                        <div>{{ row.blinkTimes.join(', ') }} 秒</div>-->
<!--                    </template>-->
<!--                </el-table-column>-->
<!--                <el-table-column label="会议记录">-->
<!--                    <template #default="{ row }">-->
<!--                        <el-collapse>-->
<!--                            <el-collapse-item v-for="(record, index) in row.records" :key="index" :title="`记录 ${record.index}`">-->
<!--                                <div><strong>发言人:</strong> {{ record.speaker }}</div>-->
<!--                                <div><strong>内容:</strong> {{ record.content }}</div>-->
<!--                                <div><strong>时间:</strong> {{ record.currentTime }}</div>-->
<!--                                <div><strong>会议时长:</strong> {{ record.meetingDuration }} 秒</div>-->
<!--                            </el-collapse-item>-->
<!--                        </el-collapse>-->
<!--                    </template>-->
<!--                </el-table-column>-->
<!--            </el-table>-->

<!--            <el-empty v-if="results.length === 0 && keyword" description="未找到相关记录" />-->
<!--        </el-card>-->
<!--    </div>-->
<!--</template>-->

<!--<script setup lang="ts" >-->
<!--import { ref } from 'vue';-->
<!--import axios from 'axios';-->
<!--import { ElMessage } from 'element-plus';-->

<!--interface Record {-->
<!--    index: number;-->
<!--    speaker: string;-->
<!--    content: string;-->
<!--    currentTime: string;-->
<!--    meetingDuration: number;-->
<!--}-->

<!--interface SearchResult {-->
<!--    records: Record[];-->
<!--    summaryText: string;-->
<!--    blinkCount: number;-->
<!--    mouthOpenCount: number;-->
<!--    blinkTimes: number[]; // 新增字段：眨眼时间-->
<!--}-->

<!--const keyword = ref('');-->
<!--const results = ref<SearchResult[]>([]);-->

<!--// 处理搜索-->
<!--const handleSearch = async () => {-->
<!--    if (!keyword.value) {-->
<!--        results.value = [];-->
<!--        return;-->
<!--    }-->

<!--    try {-->
<!--        const response = await axios.get('http://192.168.1.8:8000/search', {-->
<!--            params: { keyword: keyword.value },-->
<!--        });-->
<!--        // const response = await axios.get('http://localhost:8000/search', {-->
<!--        //     params: { keyword: keyword.value },-->
<!--        // });-->
<!--        results.value = response.data.results;-->
<!--    } catch (error) {-->
<!--        ElMessage({-->
<!--            type: 'error',-->
<!--            message: '搜索失败',-->
<!--        });-->
<!--        console.error('搜索失败:', error);-->
<!--        results.value = [];-->
<!--    }-->
<!--};-->
<!--</script>-->

<!--<style scoped lang="scss">-->
<!--.search-container {-->
<!--    padding: 20px;-->
<!--}-->

<!--.search-card {-->
<!--    max-width: 1200px;-->
<!--    margin: 0 auto;-->
<!--}-->

<!--.card-header {-->
<!--    font-size: 18px;-->
<!--    font-weight: bold;-->
<!--}-->

<!--.search-box {-->
<!--    display: flex;-->
<!--    gap: 10px;-->
<!--    margin-bottom: 20px;-->
<!--}-->
<!--</style>-->