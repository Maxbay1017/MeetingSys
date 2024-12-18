<template>
    <el-container>
        <el-header>
            <h1>声音录入</h1>
        </el-header>
        <el-main>
            <el-row>
                <el-col :span="24">
                    <el-input
                        v-model="username"
                        placeholder="请输入用户名"
                        clearable
                        style="margin-bottom: 20px"
                    />
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="8">
                    <el-button type="primary" @click="startRecording" :disabled="isRecording">
                        开始录音
                    </el-button>
                </el-col>
                <el-col :span="8">
                    <el-button type="danger" @click="stopRecording" :disabled="!isRecording">
                        停止录音
                    </el-button>
                </el-col>
                <el-col :span="8">
                    <el-button type="success" @click="uploadAudio" :disabled="!audioBlob">
                        上传音频
                    </el-button>
                </el-col>
            </el-row>
            <el-row style="margin-top: 20px">
                <el-col :span="24">
                    <el-alert
                        v-if="isRecording"
                        title="正在录音..."
                        type="warning"
                        show-icon
                        :closable="false"
                    />
                    <el-alert
                        v-if="isUploading"
                        title="正在上传..."
                        type="info"
                        show-icon
                        :closable="false"
                    />
                    <el-alert
                        v-if="uploadSuccess"
                        title="上传成功！"
                        type="success"
                        show-icon
                        :closable="false"
                    />
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script setup lang="ts" name="Recorder">
    import { ref } from 'vue';
    import { ElMessage } from 'element-plus';

    const username = ref('');
    const isRecording = ref(false);
    const isUploading = ref(false);
    const uploadSuccess = ref(false);
    const audioBlob = ref<Blob | null>(null); // 录音生成的 Blob 数据

    let mediaRecorder: MediaRecorder | null = null;

    // 开始录音
    const startRecording = async () => {
        if (!username.value) {
            ElMessage.warning('请输入用户名');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm',
                audioBitsPerSecond: 16000, // 设置采样率为 16000
            });

            mediaRecorder.ondataavailable = (event) => {
                audioBlob.value = event.data;
            };

            mediaRecorder.onstop = () => {
                isRecording.value = false;
            };

            mediaRecorder.start();
            isRecording.value = true;
        } catch (error) {
            ElMessage.error('无法开始录音，请检查麦克风权限');
            console.error(error);
        }
    };

    // 停止录音
    const stopRecording = () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
        }
    };

    // 上传音频
    const uploadAudio = async () => {
        if (!audioBlob.value) {
            ElMessage.warning('请先录音');
            return;
        }

        isUploading.value = true;
        const formData = new FormData();
        formData.append('file', audioBlob.value, `${username.value}.wav`);

        try {
            const response = await fetch('http://192.168.1.16:8000/uploadAudio2', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                uploadSuccess.value = true;
                ElMessage.success('上传成功');
            } else {
                ElMessage.error('上传失败');
            }
        } catch (error) {
            ElMessage.error(`上传失败: ${error}`);
        } finally {
            isUploading.value = false;
        }
    };
</script>

<style scoped>
.el-row {
    margin-bottom: 20px;
}
</style>