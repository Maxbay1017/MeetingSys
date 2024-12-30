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
                <el-table-column label="会议记录">
                    <template #default="{ row }">
                        <el-collapse>
                            <el-collapse-item v-for="(record, index) in row.records" :key="index" :title="`记录 ${record.index}`">
                                <div><strong>发言人:</strong> {{ record.speaker }}</div>
                                <div><strong>内容:</strong> {{ record.content }}</div>
                                <div><strong>时间:</strong> {{ record.currentTime }}</div>
                                <div><strong>会议时长:</strong> {{ record.meetingDuration }} 秒</div>
                            </el-collapse-item>
                        </el-collapse>
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
            const response = await axios.get('http://localhost:8000/search', {
                params: { keyword: keyword.value },
            });
            results.value = response.data.results;
        } catch (error) {
            console.error('搜索失败:', error);
            results.value = [];
        }
    };
</script>

<style scoped lang="scss">
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