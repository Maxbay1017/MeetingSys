<!--<template>-->
<!--    <div class="history-container">-->
<!--        <el-card class="history-card">-->
<!--            <template #header>-->
<!--                <div class="card-header">-->
<!--                    <span>会议历史记录</span>-->
<!--                </div>-->
<!--            </template>-->

<!--            <el-table :data="history" style="width: 100%" border stripe>-->
<!--                <el-table-column prop="summaryText" label="会议总结" width="300" />-->
<!--                <el-table-column prop="blinkCount" label="眨眼次数" width="120" />-->
<!--                <el-table-column prop="mouthOpenCount" label="张嘴次数" width="120" />-->
<!--                <el-table-column label="会议记录">-->
<!--                    <template #default="{ row }">-->
<!--                        <el-collapse>-->
<!--                            <el-collapse-item v-for="(record, index) in row.records" :key="index" :title="`说话人记录 ${record.index}`">-->
<!--                                <div><strong>发言人:</strong> {{ record.speaker }}</div>-->
<!--                                <div><strong>内容:</strong> {{ record.content }}</div>-->
<!--                                <div><strong>时间:</strong> {{ record.currentTime }}</div>-->
<!--                                <div><strong>会议时长:</strong> {{ record.meetingDuration }} 秒</div>-->
<!--                            </el-collapse-item>-->
<!--                        </el-collapse>-->
<!--                    </template>-->
<!--                </el-table-column>-->
<!--            </el-table>-->
<!--        </el-card>-->
<!--    </div>-->
<!--</template>-->

<!--<script setup lang='ts' name='History'>-->
<!--    import { ref, onMounted } from 'vue';-->
<!--    import axios from 'axios';-->

<!--    interface Record {-->
<!--        index: number;-->
<!--        speaker: string;-->
<!--        content: string;-->
<!--        currentTime: string;-->
<!--        meetingDuration: number;-->
<!--    }-->

<!--    interface HistoryItem {-->
<!--        records: Record[];-->
<!--        summaryText: string;-->
<!--        blinkCount: number;-->
<!--        mouthOpenCount: number;-->
<!--    }-->

<!--    const history = ref<HistoryItem[]>([]);-->

<!--    // 获取历史记录-->
<!--    const fetchHistory = async () => {-->
<!--        try {-->
<!--            const response = await axios.get('http://192.168.1.8:8000/get-history');-->
<!--            history.value = response.data.history;-->
<!--        } catch (error) {-->
<!--            console.error('获取历史记录失败:', error);-->
<!--        }-->
<!--    };-->

<!--    onMounted(() => {-->
<!--        fetchHistory();-->
<!--    });-->

<!--</script>-->

<!--<style scoped>-->
<!--    .history-container {-->
<!--        padding: 20px;-->
<!--    }-->

<!--    .history-card {-->
<!--        max-width: 1200px;-->
<!--        margin: 0 auto;-->
<!--    }-->

<!--    .card-header {-->
<!--        font-size: 18px;-->
<!--        font-weight: bold;-->
<!--    }-->
<!--</style>-->


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

<script setup lang='ts' name='History'>
import { ref, onMounted } from 'vue';
import axios from 'axios';

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
    blinkTimes: number[]; // 新增字段：眨眼时间
}

const history = ref<HistoryItem[]>([]);

// 获取历史记录
const fetchHistory = async () => {
    try {
        const response = await axios.get('http://192.168.1.8:8000/get-history');
        history.value = response.data.history;
    } catch (error) {
        console.error('获取历史记录失败:', error);
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