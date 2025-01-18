<template>
    <div class="blink-statistics-container">
        <el-card class="blink-statistics-card">
            <template #header>
                <div class="card-header">
                    <span>眨眼统计</span>
                </div>
            </template>

            <!-- 会议记录表格 -->
            <el-table :data="history" style="width: 100%" border stripe>
                <el-table-column prop="summaryText" label="会议总结" width="300" />
                <el-table-column prop="blinkCount" label="眨眼次数" width="120" />
                <el-table-column prop="mouthOpenCount" label="张嘴次数" width="120" />
                <el-table-column prop="blinkTimes" label="眨眼时间" width="200">
                    <template #default="{ row }">
                        <div>{{ row.blinkTimes.join(', ') }} 秒</div>
                    </template>
                </el-table-column>
                <el-table-column label="时间范围搜索" width="300">
                    <template #default="{ row }">
                        <div class="time-range-input">
                            <el-input v-model="row.startTime" placeholder="开始时间（秒）" style="width: 100px; margin-right: 10px;" />
                            <el-input v-model="row.endTime" placeholder="结束时间（秒）" style="width: 100px; margin-right: 10px;" />
                            <el-button type="primary" @click="calculateBlinkCount(row)">统计</el-button>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column label="统计结果" width="120">
                    <template #default="{ row }">
                        <div v-if="row.blinkCountInRange !== null">
                            {{ row.blinkCountInRange }} 次
                        </div>
                    </template>
                </el-table-column>
                <el-table-column label="会议记录">
                    <template #default="{ row }">
                        <el-collapse>
                            <el-collapse-item v-for="(record, index) in row.records" :key="index" :title="`说话人记录 ${record.index}`">
                                <div><strong>发言人:</strong> {{ record.speaker }}</div>
                                <div><strong>内容:</strong> {{ record.content }}</div>
                                <div><strong>时间:</strong> {{ record.currentTime }}</div>
                                <div><strong>会议时长:</strong> {{ record.meetingDuration }} 秒</div>
                            </el-collapse-item>
                        </el-collapse>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup lang="ts" name="BlinkStatistics">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

interface Record {
    index: number;
    speaker: string;
    content: string;
    currentTime: string;
    meetingDuration: number;
}

interface HistoryItem {
    records: Record[];
    summaryText: string;
    blinkCount: number;
    mouthOpenCount: number;
    blinkTimes: number[]; // 眨眼时间
    startTime?: number; // 搜索开始时间
    endTime?: number; // 搜索结束时间
    blinkCountInRange?: number; // 统计结果
}

const history = ref<HistoryItem[]>([]);

// 获取历史记录
const fetchHistory = async () => {
    try {
        const response = await axios.get('http://192.168.1.17:8000/get-history');
        history.value = response.data.history.map((item: HistoryItem) => ({
            ...item,
            startTime: undefined, // 初始化开始时间
            endTime: undefined, // 初始化结束时间
            blinkCountInRange: null, // 初始化统计结果
        }));
    } catch (error) {
        console.error('获取历史记录失败:', error);
    }
};

// 计算指定时间范围内的眨眼次数
const calculateBlinkCount = (row: HistoryItem) => {
    const start = parseInt(row.startTime as any);
    const end = parseInt(row.endTime as any);

    if (isNaN(start) || isNaN(end) || start < 0 || end < 0 || start > end) {
        ElMessage.error('请输入有效的时间范围');
        return;
    }

    const blinkTimesInRange = row.blinkTimes.filter((time) => time >= start && time <= end);
    row.blinkCountInRange = blinkTimesInRange.length;
};

onMounted(() => {
    fetchHistory();
});
</script>

<style scoped>
.blink-statistics-container {
    padding: 20px;
}

.blink-statistics-card {
    max-width: 1200px;
    margin: 0 auto;
}

.card-header {
    font-size: 18px;
    font-weight: bold;
}

.time-range-input {
    display: flex;
    align-items: center;
}
</style>