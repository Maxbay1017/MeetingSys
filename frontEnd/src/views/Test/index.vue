<template>
  <div class="container" >
    <div class="left">
      <div class="meetingVideo">
        <video  ref="videoRef" autoplay style="background: #7f7f7f; width:80%;height: 80%;justify-content: center;align-content: center"></video>
      </div>
    </div>
    <div class="right">
        <div class="info">
          <div class="buttonList">
              <el-button class="video_open" type="primary" @click="toggleOpeningVideo" >
                  {{!isOpening?'打开视频':'关闭视频'}}
              </el-button>
              <el-button class="connect_backEnd" type="primary" @click="toggleConnecting">
                  {{!isConnecting?'连接后端':'断开连接'}}
              </el-button>
              <el-button class="record_audio" type="primary" @click="toggleRecording">
                  {{ isRecording ? '停止录音' : '开始录音' }}
              </el-button>

          </div>

          <div class="faceInfo " >
            <el-card>眨眼次数:{{blinkCount}} </el-card>
            <el-card style="margin-top: 10px">张嘴次数:{{mouthOpenCount}} </el-card>
          </div>
      </div>
        <div class="speakerInfo">
            <el-card style="height:50px;width: 80% " v-for="(record, index) in visibleRecords" :key="index">
                <strong>{{ record.speaker }}:</strong> {{ record.content }}
            </el-card>
        </div>


    </div>
  </div>
</template>

<script setup lang="ts" name="Test">
  import {ref,onMounted,onUnmounted,computed} from "vue";
  import {ElMessage} from "element-plus";
  const ws=ref<WebSocket|null>(null);
  const videoRef=ref<HTMLVideoElement|null>(null);
  const blinkCount=ref<number>(0);                     //眨眼计数
  const mouthOpenCount=ref<number>(0);                 //张嘴计数
  let frameInterval:number|null;
  let buttonIndex=ref<number>(1);
  let tmp=ref<boolean>(false)// 打开视频按钮是否打开

  const audioWs = ref<WebSocket | null>(null);

  const transcriptionResult = ref<HTMLElement | null>(null);

  const isOpening=ref<boolean>(false);
  const isConnecting=ref<boolean>(false);
  const isRecording = ref<boolean>(false);

  let audioInterval: number | null = null;
  let record: Recorder | null = null;

  interface Message {
      speaker: string;
      content: string;
  }

  const records =ref<Message[]>([]);

  const visibleRecords = computed(() => {
      return records.value.slice(-5);
  });

  //TODO 打开视频按钮
  const openVideo=()=>{
    initCamera();
    tmp.value=true;
    ElMessage({
      type:'success',
      message:'摄像头打开成功'
    })
  }

  //TODO 关闭视频按钮
  const closeVideo = () => {
    if (videoRef.value && videoRef.value.srcObject) {
      const stream: MediaStream = videoRef.value.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.value.srcObject = null;
      tmp.value=false;
      ElMessage({
        type:'success',
        message:'摄像头关闭成功'
      })
    }
};

  //TODO 初始化相机
  const  initCamera=async ()=>{
    try {
      const stream=await navigator.mediaDevices.getUserMedia({video:true});
      if(videoRef.value){
        videoRef.value.srcObject=stream;
        videoRef.value.addEventListener('playing',()=>{});
      }
    }catch (error){
      ElMessage({
        type:'fail',
        message:error
      })
    }
  }

  // TODO 发送帧
  const sendFrame=()=>{
    if(tmp.value==true && videoRef.value && ws.value && ws.value.readyState==WebSocket.OPEN){
      const canvas=document.createElement('canvas');
      const context=canvas.getContext('2d');
      if(context){
        canvas.width=videoRef.value.videoWidth;
        canvas.height=videoRef.value.videoHeight;
        context.drawImage(videoRef.value!,0,0,canvas.width,canvas.height);
        const imageData=canvas.toDataURL('image/jpeg');
        // console.log(imageData)
        if(imageData.startsWith('data:image/jpeg;base64')){
          ws.value.send(imageData);
        }else{
          // ElMessage({
          //   type:'error',
          //   message:'图像数据无效'
          // })
        }
      }
    }
    frameInterval=setTimeout(sendFrame,100);
  }
  
  // TODO 视频连接后端
  const connect=()=>{
      if(tmp.value==false){
          ElMessage({
              type:'error',
              message:'请打开摄像头'
          })
      }else {
          ws.value=new WebSocket('ws://192.168.1.4:8000/ws');
          // ws.value=new WebSocket('ws://192.168.1.21:8000/ws');
          // ws.value=new WebSocket('ws://localhost:8000/ws');
          ws.value.onopen=()=>{
              sendFrame();
          }
          ws.value.onmessage=(event)=>{
              const data=JSON.parse(event.data);
              console.log(data)
              if(data.event){
                  if(data.event==='blink'){
                      blinkCount.value+=1;
                  }
                  if(data.event==='mouth_open'){
                      mouthOpenCount.value+=1;
                  }
              }else{
                  // console.log('JSON解析错误')
                  // ElMessage({
                  //     type:'error',
                  //     message:'JSON 解析出错'
                  // })
              }
          }
      }
  }



  // TODO 视频与后端连接断开
  const disconnect=()=>{
      ws.value.close();
  }

  // TODO  切换打开视频按钮
  const toggleOpeningVideo=()=>{
      if(!isOpening.value){
          openVideo();
          isOpening.value=true;
      }else{
          closeVideo();
          isOpening.value=false;
      }
  }

  // TODO 切换是否连接按钮
  const toggleConnecting = () => {
    if(!isConnecting.value){
        connect();
        isConnecting.value=true;
    }else{
        disconnect();
        isConnecting.value=false;
    }
  }


  // TODO 切换录音状态
  const toggleRecording = () => {
      if (!isRecording.value) {
          startRecording();
      } else {
          stopRecording();
      }
  };

  // TODO 开始录音
  const startRecording = () => {
      // const speakerVerificationCheckbox = document.getElementById('speakerVerification') as HTMLInputElement;
      const sv = 1;
      const lang='auto'
      // const lang = (document.getElementById("lang") as HTMLInputElement).value;

      // 构造查询参数
      const queryParams = [];
      if (lang) {
          queryParams.push(`lang=${lang}`);
      }
      if (sv) {
          queryParams.push('sv=1');
      }
      const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
      audioWs.value = new WebSocket(`ws://192.168.1.4:8000/ws/transcribe_test${queryString}`);
      // audioWs.value = new WebSocket(`ws://192.168.1.21:8000/ws/transcribe_test${queryString}`);
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
                  records.value.push({'speaker':resJson.speaker,'content':resJson.data})
                  console.log(resJson.speaker,":",resJson.data)
                  // transcriptionResult.value!.textContent += "\n" + (resJson.data || 'No speech recognized');
              }
          } catch (e) {
              // transcriptionResult.value!.textContent += "\n" + evt.data;
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

  // TODO 停止录音
  const stopRecording = () => {
      if (audioWs.value) {
          audioWs.value.close();
          record!.stop();
          clearInterval(audioInterval!);
      }
      isRecording.value = false;
  };

  // TODO 初始化录音
  const initRecorder = (stream: MediaStream) => {
      record = new Recorder(stream);
  };

  // TODO 初始化
  onMounted(async () => {
      transcriptionResult.value = document.getElementById('transcriptionResult') as HTMLElement;
      try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          initRecorder(stream);
      } catch (error) {
          ElMessage({
              type: 'error',
              message: '无法获取音频输入'
          });
      }
  });

  // TODO 组件销毁
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
              }
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
              let accum = 0, count = 0;
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
  .container{
    display: flex;
    height: 80vh;
    .left{
      flex: 6;
      .meetingVideo{
        width: 100%;
        height: 100%;
      }
    }
    .right{
        height: 100%;
        flex: 4;
      .info{
          margin-top: 10px;
          height: 60%;
          display: flex;
        .buttonList{
          width:100px;
          height: 100%;
          display: flex;
          flex-direction: column;
          flex-wrap: wrap;
          .video_open{
            width: 100%;
            height: 50px;
          }
          //.video_close{
          //  margin: 10px 0px;
          //  width: 100%;
          //  height: 50px;
          //}
          .connect_backEnd{
            margin: 10px 0px;
            //margin-left: 0px;
            width: 100%;
            height: 50px;
          }

          .close_connect{
            //margin: 10px 0px;
            margin-top: 10px;
            margin-left: 0px;
            width: 100%;
            height: 50px;
          }
            .record_audio {
                //margin-top: 10px;
                margin-left: 0px;
                width: 100%;
                height: 50px;
            }
        }
        .faceInfo{
          margin-left: 30px;
          height: 100%;

        }
      }
        .speakerInfo{
            margin-top: 20px;
            height: 30%;
        }

    }
  }
</style>