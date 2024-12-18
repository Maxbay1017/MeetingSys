<template>
  <div>
    <video ref="videoRef" autoplay></video>
    <p>眨眼次数: {{ blinkCount }}</p>
    <p>张嘴次数: {{ mouthOpenCount }}</p>
  </div>
</template>

<script setup lang="ts" name="home">
  import { ref, onMounted, onUnmounted } from 'vue';

  const ws = ref<WebSocket | null>(null);
  const videoRef = ref<HTMLVideoElement | null>(null);
  const blinkCount = ref(0);
  const mouthOpenCount = ref(0);
  let frameInterval: number | undefined;

  onMounted(() => {
    initCamera();
    ws.value = new WebSocket('ws://localhost:8000/ws');

    ws.value.onopen = () => {
      sendFrame();
    };

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event) {
          if (data.event === 'blink') {
            blinkCount.value += 1;
          } else if (data.event === 'mouth_open') {
            mouthOpenCount.value += 1;
          }
        } else {
          console.log('mouth open:', data.is_mouth_open, 'MAR:', data.mar, 'EAR:', data.ear);
        }
      } catch (e) {
        console.error('Error parsing JSON:', e);
      }
    };
  });

  const initCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.value) {
        videoRef.value.srcObject = stream;
        videoRef.value.addEventListener('playing', () => {
          // 确保视频开始播放后再发送帧
        });
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const sendFrame = () => {
    if (videoRef.value && ws.value && ws.value.readyState === WebSocket.OPEN) {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (context) {
        canvas.width = videoRef.value.videoWidth;
        canvas.height = videoRef.value.videoHeight;
        context.drawImage(videoRef.value!, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        if (imageData.startsWith('data:image/jpeg;base64')) {
          ws.value.send(imageData);
        } else {
          console.error('Invalid image data:', imageData);
        }
      }
    }
    frameInterval = setTimeout(sendFrame, 100); // 每100ms发送一次
  };

    onUnmounted(() => {
      if (frameInterval) {
        clearTimeout(frameInterval);
      }
      if (ws.value) {
        ws.value.close();
      }
  });
</script>
<style lang="scss">

</style>
