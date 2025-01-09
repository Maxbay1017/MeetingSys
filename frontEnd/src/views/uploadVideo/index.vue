<template>
    <div class="container">
        <div class="left">
            <!-- 视频上传和播放组件 -->
            <div class="meetingVideo">
                <input type="file" accept="video/*" @change="handleVideoUpload" />
                <video ref="videoPlayer" controls style="background: #F0F8FF; width: 80%; height: 80%;"></video>
            </div>
            <div class="summary-section">
                <textarea v-model="summaryText" placeholder="会议记录..." class="summary-textarea"></textarea>
                <button @click="generateSummary" class="generate-button">生成总结</button>
            </div>
        </div>
        <div class="right">
            <div class="info">
                <div class="buttonList">
                    <!-- 保留其他按钮 -->
                    <el-button class="record_audio" type="primary" @click="toggleRecording">
                        {{ isRecording ? '停止录音' : '开始录音' }}
                    </el-button>
                    <el-button class="faceInfo" type="primary" @click="toggleFace">
                        {{ isFacing ? '关闭面部特征' : '显示面部特征' }}
                    </el-button>
                    <el-button
                        class="generateReport"
                        type="primary"
                        :disabled="!(records && blinkCount && mouthOpenCount && summaryText)"
                        @click="generateReport">
                        点击生成报告
                    </el-button>
                    <el-button class="savaData" type="primary" @click="saveData">
                        点击保存
                    </el-button>
                </div>
                <!-- 显示眨眼和张嘴次数 -->
                <div v-if="isFacing" class="faceInfo">
                    <el-card>眨眼次数: {{ blinkCount }}</el-card>
                    <el-card style="margin-top: 10px">张嘴次数: {{ mouthOpenCount }}</el-card>
                </div>
            </div>
            <!-- 显示会议记录 -->
            <div class="speakerInfo">
                <el-card style="height: 50px; width: 80%" v-for="(record, index) in visibleRecords" :key="index">
                    <strong>{{ record.currentTime }}: {{ record.speaker }}:</strong> {{ record.content }}
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts" name="UploadVideo">
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const videoPlayer = ref<HTMLVideoElement | null>(null);
const blinkCount = ref<number>(0);
const mouthOpenCount = ref<number>(0);
const isFacing = ref<boolean>(false);
const summaryText = ref<string>('');
const isRecording = ref<boolean>(false);
const records = ref<any[]>([]);
const ws = ref<WebSocket | null>(null);

// 处理视频上传
const handleVideoUpload = async (event: Event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    // 播放视频
    if (videoPlayer.value) {
        const videoUrl = URL.createObjectURL(file);
        videoPlayer.value.src = videoUrl;
        videoPlayer.value.play();

        // 逐帧处理视频
        processVideoFrames(videoPlayer.value);
    }
};

// 逐帧处理视频
const processVideoFrames = (video: HTMLVideoElement) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return;

    const sendFrame = () => {
        if (video.paused || video.ended) return;

        // 绘制当前帧到 canvas
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // 将帧转换为 base64
        const imageData = canvas.toDataURL('image/jpeg');
        if (ws.value && ws.value.readyState === WebSocket.OPEN) {
            ws.value.send(imageData);
        }

        // 继续处理下一帧
        requestAnimationFrame(sendFrame);
    };

    // 开始处理
    sendFrame();
};

// 初始化 WebSocket 连接
const initWebSocket = () => {
    ws.value = new WebSocket('ws://192.168.1.8:8000/ws');
    ws.value.onopen = () => {
        ElMessage.success("WebSocket 连接成功");
    };
    ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.event) {
            if (data.event === 'blink') {
                blinkCount.value += 1;
            }
            if (data.event === 'mouth_open') {
                mouthOpenCount.value += 1;
            }
        }
    };
    ws.value.onclose = () => {
        ElMessage.warning("WebSocket 连接关闭");
    };
    ws.value.onerror = (error) => {
        ElMessage.error(`WebSocket 错误: ${error}`);
    };
};

// 生成总结
const generateSummary = async () => {
    if (records.value.length === 0) {
        ElMessage.warning('请先提供会议记录');
        return;
    }
    try {
        const response = await axios.post('http://192.168.1.8:8000/generate-summary', {
            records: records.value,
        });

        if (response.status === 200) {
            summaryText.value = response.data.summary;
            ElMessage.success('总结生成成功');
        } else {
            ElMessage.error('总结生成失败');
        }
    } catch (error) {
        ElMessage.error(`总结生成失败: ${error}`);
    }
};

// 生成报告
const generateReport = async () => {
    try {
        const response = await axios.post('http://192.168.1.8:8000/generate-pdf', {
            records: records.value,
            summaryText: summaryText.value,
            blinkCount: blinkCount.value,
            mouthOpenCount: mouthOpenCount.value,
        }, {
            responseType: 'blob',
        });

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'report.pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        ElMessage.error('生成报告失败');
    }
};

// 保存数据
const saveData = async () => {
    try {
        const response = await axios.post('http://192.168.1.8:8000/save-data', {
            records: records.value,
            summaryText: summaryText.value,
            blinkCount: blinkCount.value,
            mouthOpenCount: mouthOpenCount.value,
        });

        if (response.status === 200) {
            ElMessage.success('保存成功');
        } else {
            ElMessage.error('保存失败');
        }
    } catch (error) {
        ElMessage.error('保存失败');
    }
};

// 初始化 WebSocket
onMounted(() => {
    initWebSocket();
});

// 清理 WebSocket
onUnmounted(() => {
    if (ws.value) {
        ws.value.close();
    }
});
</script>

<style scoped lang="scss">
.container {
    display: flex;
    height: 80vh;
    .left {
        flex: 6;
        .meetingVideo {
            width: 80%;
            height: 80%;
            background: #F0F8FF;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(30, 144, 255, 0.1);
                pointer-events: none;
            }

            video {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
        }

        .summary-section {
            width: 80%;
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;

            .summary-textarea {
                width: 100%;
                height: 100px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 10px;
                font-size: 14px;
                resize: none;
                background: #F0F8FF;
                color: #333;
            }

            .generate-button {
                margin-top: 3px;
                padding: 10px 20px;
                background: #1E90FF;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;

                &:hover {
                    background: #007BFF;
                }
            }
        }
    }
    .right {
        height: 100%;
        flex: 4;
        .info {
            margin-top: 10px;
            height: 60%;
            display: flex;
            .buttonList {
                width: 100px;
                height: 100%;
                display: flex;
                flex-direction: column;
                flex-wrap: wrap;
                .record_audio {
                    margin-left: 0px;
                    width: 100%;
                    height: 50px;
                }
                .faceInfo {
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }
                .generateReport {
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }
                .savaData {
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }
            }
            .faceInfo {
                margin-left: 30px;
                height: 100%;
            }
        }
        .speakerInfo {
            margin-top: 20px;
            height: 30%;
        }
    }
}
</style>