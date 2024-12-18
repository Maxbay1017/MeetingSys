<template>
  <div class="voice-recorder">
    <div class="voice-bar" ref="voiceBar">
      <!-- 这里将显示波浪效果 -->
    </div>
    <button @click="toggleRecording">{{ isRecording ? '停止录音' : '开始录音' }}</button>
  </div>
</template>

<script setup lang="ts" name="VoiceRecorder">
import { ref, onMounted, onUnmounted } from 'vue';
import WaveSurfer from 'wavesurfer.js';

const isRecording = ref(false);
const voiceBar = ref<HTMLElement | null>(null);
let mediaRecorder: MediaRecorder | null = null;
let wavesurfer: WaveSurfer | null = null;
let audioChunks: Blob[] = [];

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
};

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      if (wavesurfer) {
        wavesurfer.loadBlob(audioBlob);
      }
      audioChunks = [];
    };
    mediaRecorder.start();
    isRecording.value = true;
  } catch (error) {
    console.error('无法获取麦克风权限:', error);
  }
};

const stopRecording = () => {
  if (mediaRecorder) {
    mediaRecorder.stop();
    isRecording.value = false;
  }
};

onMounted(() => {
  if (voiceBar.value) {
    wavesurfer = WaveSurfer.create({
      container: voiceBar.value,
      waveColor: 'violet',
      progressColor: 'purple',
      barWidth: 2,
      height: 50,
    });
  }
});

onUnmounted(() => {
  if (wavesurfer) {
    wavesurfer.destroy();
  }
});
</script>

<style scoped>
.voice-recorder {
  display: flex;
  align-items: center;
}

.voice-bar {
  width: 200px;
  height: 50px;
  margin-right: 10px;
  border: 1px solid #ccc;
}

button {
  padding: 10px 20px;
  cursor: pointer;
}
</style>