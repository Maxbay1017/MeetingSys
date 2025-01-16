<template>
    <div class="container">
        <div class="left">
            <div class="meetingVideo">
                <video v-if="uploadedVideoUrl" ref="videoRef" :src="uploadedVideoUrl" autoplay controls style="background: #F0F8FF; width:80%;height: 80%;justify-content: center;align-content: center"></video>
                <input type="file" @change="handleVideoUpload" accept="video/*" style="display: none;" ref="videoUploadInput">
                <button @click="triggerVideoUpload" class="upload-button">上传视频</button>
            </div>
            <div class="summary-section">
                <textarea v-model="summaryText" placeholder="会议记录..." class="summary-textarea"></textarea>
                <button @click="generateSummary" class="generate-button">生成总结</button>
            </div>
        </div>
        <div class="right">
            <div class="info">
                <div class="buttonList">
                    <el-button class="connect_backEnd" type="primary" @click="toggleConnecting">
                        {{!isConnecting?'连接后端':'断开连接'}}
                    </el-button>
                    <el-button class="record_audio" type="primary" @click="toggleRecording">
                        {{ isRecording ? '停止录音' : '开始录音' }}
                    </el-button>
                    <el-button class="faceInfo" type="primary" @click="toggleFace">
                        {{isFacing?'关闭面部特征':'显示面部特征'}}
                    </el-button>

                    <el-button
                        class="generateReport"
                        type="primary"
                        :disabled="!(records && blinkCount && mouthOpenCount && summaryText)"
                        @click="generateReport">
                        点击生成报告
                    </el-button>

                    <el-button class="savaData"
                               type="primary"
                               :disabled="!(records && blinkCount && mouthOpenCount && summaryText)"
                               @click="saveData">
                        点击保存
                    </el-button>
                </div>

                <div v-if="isFacing" class="faceInfo ">
                    <el-card>眨眼次数:{{blinkCount}} </el-card>
                    <el-card style="margin-top: 10px">张嘴次数:{{mouthOpenCount}} </el-card>
                </div>
            </div>
            <div class="speakerInfo">
                <el-card style="height:50px;width: 80% " v-for="(record, index) in visibleRecords" :key="index">
                    <strong>{{record.currentTime}}:{{ record.speaker }}:</strong> {{ record.content }}
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts" name="UploadVideo2">
import { ref, onMounted, onUnmounted, computed } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

// WebSocket 相关
const ws = ref<WebSocket | null>(null);
const audioWs = ref<WebSocket | null>(null);

// 视频相关
const videoRef = ref<HTMLVideoElement | null>(null);
const uploadedVideoUrl = ref<string | null>(null); // 上传的视频URL
let frameInterval: number | null = null; // 视频帧发送间隔
let tmp = ref<boolean>(false); // 视频是否打开

// 面部特征相关
const blinkCount = ref<number>(0); // 眨眼计数
const mouthOpenCount = ref<number>(0); // 张嘴计数
const isFacing = ref<boolean>(false); // 是否显示面部特征

// 会议记录相关
interface Message {
    index: number;
    speaker: string;
    content: string;
    currentTime: string;
    meetingDuration: number;
}
const records = ref<Message[]>([]); // 会议记录
const visibleRecords = computed(() => records.value.slice(-5)); // 可见的会议记录
let cnt = ref<number>(0); // 会议记录计数
let msgTmp: Message = { // 临时存储会议记录
    index: 0,
    speaker: '',
    content: '',
    currentTime: '',
    meetingDuration: 0
};

// 用户相关
let userId = ref<number>(0); // 用户ID
let userName = ref<string>("zy"); // 用户名

// 会议状态相关
const meetingStartTime = ref<number>(0); // 会议开始时间（时间戳）
const isMeetingStarted = ref<boolean>(false); // 会议是否已开始

// 录音相关
let audioInterval: number | null = null; // 录音数据发送间隔
let record: Recorder | null = null; // 录音器对象
const isRecording = ref<boolean>(false); // 是否正在录音

// 总结和报告相关
const summaryText = ref<string>(''); // 会议总结文本
const pdfGenerated = ref<boolean>(false); // PDF 是否已生成

// 连接状态相关
const isConnecting = ref<boolean>(false); // 是否连接后端

// 上传视频
const handleVideoUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
        const file = input.files[0];
        uploadedVideoUrl.value = URL.createObjectURL(file);

        // 读取视频文件并发送帧
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        video.onloadedmetadata = () => {
            // video.play();
            processVideoFrames(video);
        };
    }
};

const triggerVideoUpload = () => {
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    input.click();
};

// 处理视频帧
const processVideoFrames = (video: HTMLVideoElement) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return;

    const sendFrame = () => {
        if (video.paused || video.ended) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');

        if (ws.value && ws.value.readyState === WebSocket.OPEN) {
            ws.value.send(imageData);
        }

        requestAnimationFrame(sendFrame);
    };

    video.addEventListener('play', () => {
        sendFrame();
    });
};

// 连接后端
const connect = () => {
    if (!uploadedVideoUrl.value) {
        ElMessage.error('请先上传视频');
        return;
    }

    ws.value = new WebSocket('ws://192.168.1.8:8000/ws');
    ws.value.onopen = () => {
        ElMessage.success('连接后端成功');
        isConnecting.value = true;
    };

    ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.event === 'blink') {
            blinkCount.value += 1;
        } else if (data.event === 'mouth_open') {
            mouthOpenCount.value += 1;
        } else if (data.speaker && data.content) {
            const currentTime = new Date().toLocaleString('zh-CN', {
                timeZone: 'Asia/Shanghai',
                hour12: false,
            }).replace(/\//g, '-');

            records.value.push({
                index: records.value.length + 1,
                speaker: data.speaker,
                content: data.content,
                currentTime: currentTime,
                meetingDuration: Math.floor((Date.now() - meetingStartTime.value) / 1000),
            });
        }
    };

    ws.value.onclose = () => {
        ElMessage.warning('连接已关闭');
        isConnecting.value = false;
    };

    ws.value.onerror = (error) => {
        ElMessage.error('连接出错');
        console.error('WebSocket error:', error);
    };
};

// 断开连接
const disconnect = () => {
    if (ws.value) {
        ws.value.close();
        isConnecting.value = false;
    }
};

// 切换连接状态
const toggleConnecting = () => {
    if (!isConnecting.value) {
        connect();
    } else {
        disconnect();
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

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'report.pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('生成报告失败:', error);
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

// 切换录音状态
const toggleRecording = () => {
    if (!isRecording.value) {
        startRecording();
    } else {
        stopRecording();
    }
};

// 开始录音
const startRecording = () => {
    const sv = 1;
    const lang = 'auto';

    // 构造查询参数
    const queryParams = [];
    if (lang) {
        queryParams.push(`lang=${lang}`);
    }
    if (sv) {
        queryParams.push('sv=1');
    }
    const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
    audioWs.value = new WebSocket(`ws://192.168.1.8:8000/ws/transcribe_test${queryString}`);
    audioWs.value.binaryType = 'arraybuffer';
    audioWs.value.onopen = () => {
        record!.start();
        audioInterval = setInterval(() => {
            if (audioWs.value && audioWs.value.readyState === 1) {
                const audioBlob = record!.getBlob();
                const reader = new FileReader();
                reader.onloadend = () => {
                    audioWs.value!.send(audioBlob);
                    record!.clear();
                };
                reader.readAsArrayBuffer(audioBlob);
            }
        }, 500);
    };

    audioWs.value.onmessage = (evt) => {
        try {
            const resJson = JSON.parse(evt.data);
            if (resJson.code === 0) {
                const currentTimestamp = Date.now();
                const meetingDuration = Math.floor((currentTimestamp - meetingStartTime.value) / 1000); // 计算会议开启时长（秒）

                const currentTime = new Date(currentTimestamp).toLocaleString('zh-CN', {
                    timeZone: 'Asia/Shanghai', // 设置为北京时间时区
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false, // 使用 24 小时制
                }).replace(/\//g, '-'); // 将斜杠替换为横杠

                // TODO  逻辑  如果说话人==userName
                msgTmp.speaker = resJson.speaker;
                msgTmp.content = resJson.data;
                msgTmp.currentTime = currentTime;
                msgTmp.meetingDuration = meetingDuration;

                console.log(msgTmp);
                cnt.value += 1;
                records.value.push({
                    index: cnt.value,
                    speaker: resJson.speaker,
                    content: resJson.data,
                    currentTime: currentTime,
                    meetingDuration: meetingDuration,
                });
            }
        } catch (e) {
            console.error('解析音频数据失败:', e);
        }
    };

    audioWs.value.onclose = () => {
        console.log('WebSocket connection closed');
    };

    audioWs.value.onerror = (error) => {
        console.error('WebSocket error: ', error);
    };

    isRecording.value = true;
};

// 停止录音
const stopRecording = () => {
    if (audioWs.value) {
        audioWs.value.close();
        record!.stop();
        clearInterval(audioInterval!);
    }
    isRecording.value = false;
};

// 初始化录音
const initRecorder = (stream: MediaStream) => {
    record = new Recorder(stream);
};

// 初始化
onMounted(async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        initRecorder(stream);
    } catch (error) {
        ElMessage({
            type: 'error',
            message: '无法获取音频输入',
        });
    }
});

// 组件销毁
onUnmounted(() => {
    if (ws.value) {
        ws.value.close();
    }
    if (audioWs.value) {
        audioWs.value.close();
    }
    if (frameInterval) {
        clearTimeout(frameInterval);
    }
    if (audioInterval) {
        clearInterval(audioInterval);
    }
});

// Recorder 类
class Recorder {
    private sampleBits: number;
    private inputSampleRate: number;
    private outputSampleRate: number;
    private channelCount: number;
    private context: AudioContext;
    private audioInput: MediaStreamAudioSourceNode;
    private recorder: ScriptProcessorNode;
    private audioData: {
        size: number;
        buffer: Float32Array[];
        inputSampleRate: number;
        inputSampleBits: number;
        clear: () => void;
        input: (data: Float32Array) => void;
        encodePCM: () => Blob;
    };

    constructor(stream: MediaStream) {
        this.sampleBits = 16; // 采样位数
        this.inputSampleRate = 48000; // 输入采样率
        this.outputSampleRate = 16000; // 输出采样率
        this.channelCount = 1; // 单声道
        this.context = new AudioContext();
        this.audioInput = this.context.createMediaStreamSource(stream);
        this.recorder = this.context.createScriptProcessor(4096, this.channelCount, this.channelCount);

        this.audioData = {
            size: 0,
            buffer: [],
            inputSampleRate: this.inputSampleRate,
            inputSampleBits: this.sampleBits,
            clear: () => {
                this.audioData.buffer = [];
                this.audioData.size = 0;
            },
            input: (data: Float32Array) => {
                this.audioData.buffer.push(new Float32Array(data));
                this.audioData.size += data.length;
            },
            encodePCM: () => {
                const bytes = new Float32Array(this.audioData.size);
                let offset = 0;
                for (let i = 0; i < this.audioData.buffer.length; i++) {
                    bytes.set(this.audioData.buffer[i], offset);
                    offset += this.audioData.buffer[i].length;
                }
                const dataLength = bytes.length * (this.sampleBits / 8);
                const buffer = new ArrayBuffer(dataLength);
                const data = new DataView(buffer);
                offset = 0;
                for (let i = 0; i < bytes.length; i++, offset += 2) {
                    const s = Math.max(-1, Math.min(1, bytes[i]));
                    data.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                }
                return new Blob([data], { type: 'audio/pcm' });
            },
        };

        this.recorder.onaudioprocess = (e) => {
            const resampledData = this.downsampleBuffer(e.inputBuffer.getChannelData(0), this.inputSampleRate, this.outputSampleRate);
            this.audioData.input(resampledData);
        };
    }

    start() {
        this.audioInput.connect(this.recorder);
        this.recorder.connect(this.context.destination);
    }

    stop() {
        this.recorder.disconnect();
    }

    getBlob() {
        return this.audioData.encodePCM();
    }

    clear() {
        this.audioData.clear();
    }

    private downsampleBuffer(buffer: Float32Array, inputSampleRate: number, outputSampleRate: number) {
        if (outputSampleRate === inputSampleRate) {
            return buffer;
        }
        const sampleRateRatio = inputSampleRate / outputSampleRate;
        const newLength = Math.round(buffer.length / sampleRateRatio);
        const result = new Float32Array(newLength);
        let offsetResult = 0;
        let offsetBuffer = 0;
        while (offsetResult < result.length) {
            const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
            let accum = 0,
                count = 0;
            for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
                accum += buffer[i];
                count++;
            }
            result[offsetResult] = accum / count;
            offsetResult++;
            offsetBuffer = nextOffsetBuffer;
        }
        return result;
    }
}
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

            video {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .upload-button {
                margin-top: 10px;
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

                .connect_backEnd {
                    margin: 10px 0px;
                    width: 100%;
                    height: 50px;
                }

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