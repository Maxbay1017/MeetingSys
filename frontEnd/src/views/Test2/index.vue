<template>
    <div class="container" >
        <div class="left">
            <div class="meetingVideo">
                <video  ref="videoRef" autoplay style="background:  #F0F8FF; width:80%;height: 80%;justify-content: center;align-content: center"></video>
            </div>
            <div class="summary-section">
                <textarea v-model="summaryText" placeholder="会议记录..." class="summary-textarea"></textarea>
                <button @click="generateSummary" class="generate-button">生成总结</button>
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

<script setup lang="ts" name="Test2">
    import {ref,onMounted,onUnmounted,computed,watch} from "vue";
    import axios from "axios";
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

    const isOpening=ref<boolean>(false);    // 睁眼此时
    const isConnecting=ref<boolean>(false);
    const isRecording = ref<boolean>(false);
    const isFacing=ref<boolean>(false);

    let audioInterval: number | null = null;//audioInterval 计时器帧
    let record: Recorder | null = null;//录音器对象

    let userId=ref<number>(0);     //用户的id
    let userName=ref<String>("zy");  //用户的名字

    let cnt=ref<number>(0)

    const summaryText = ref(''); //文本框内容

    const pdfGenerated = ref(false);//pdf是否创建


    const meetingStartTime = ref<number>(0); // 会议开始时间（时间戳）
    const isMeetingStarted = ref(false); // 会议是否已开始



    interface Message {
        index:number,
        speaker: string;
        content: string;
        currentTime: string;
        meetingDuration: number;
    }


    const records =ref<Message[]>([]);

    const visibleRecords = computed(() => {
        return records.value.slice(-5);
    });

    let changeCount = 0;
    let timer: number | null = null;

    let msgTmp:Message={
        index:0,
        speaker:'',
        content:'',
        currentTime:'',
        meetingDuration:0
    };



    // TODO 点击生成报告
    const generateReport = async () => {
        try {
            // 发送数据到后端
            const response = await axios.post('http://192.168.1.8:8000/generate-pdf', {
                records: records.value,
                summaryText: summaryText.value,
                blinkCount: blinkCount.value,
                mouthOpenCount: mouthOpenCount.value,
            }, {
                responseType: 'blob',  // 指定响应类型为 blob
            });

            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'report.pdf');  // 设置下载文件名
            document.body.appendChild(link);
            link.click();

            // 移除链接
            document.body.removeChild(link);
        } catch (error) {
            console.error('生成报告失败:', error);
        }
    };



    // TODO 是否显示面部信息
    const toggleFace=()=>{
        isFacing.value=!isFacing.value;
    }


    // TODO 监听事件， 如果2s内，用户的嘴巴张嘴表示，此时是用户说话，
    // watch(mouthOpenCount, (newValue, oldValue) => {
    //     if (newValue > oldValue) {
    //         changeCount++;
    //         if (changeCount >= 2) {
    //             // TODO 判断事先设定的用户名与后端判定的用户名是否相同
    //             if(msgTmp.speaker==userName.value){
    //                 records.value.push({'speaker':msgTmp.speaker,'content':msgTmp.content});
    //                 ElMessage({
    //                     type:'success',
    //                     message:'添加成功'
    //                 })
    //                 msgTmp.speaker='';
    //                 msgTmp.content='';
    //             }
    //             changeCount = 0;
    //             if (timer) {
    //                 clearTimeout(timer);
    //             }
    //         }
    //         if (timer) clearTimeout(timer);
    //         timer = setTimeout(() => {
    //             changeCount = 0;
    //             timer = null;
    //         }, 2000);
    //     }
    // });




    // TODO 保存数据至MongoDB
    const saveData = async () => {
        try {
            const response = await axios.post('http://localhost:8000/save-data', {
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



    //TODO  生成总结的函数
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
        } finally {

        }
    };


    // const generateSummary = async () => {
    //     try {
    //         // 将 records 发送到后端
    //         const response = await axios.post('http://localhost:8000/generate-summary', {
    //             records: records.value,
    //         });
    //
    //         // 更新文本框内容为生成的总结
    //         summaryText.value = response.data.summary;
    //     } catch (error) {
    //         console.error('生成总结失败:', error);
    //         summaryText.value = '生成总结失败，请重试。';
    //     }
    // };



    //TODO 打开视频按钮
    const openVideo=()=>{
        initCamera();
        tmp.value=true;

        //  TODO 默认打开视频就是会议开启
        isMeetingStarted.value=true;
        meetingStartTime.value = Date.now(); // 记录会议开始时间（时间戳）


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
            // ws.value=new WebSocket('ws://192.168.1.16:8000/ws');
            ws.value=new WebSocket('ws://192.168.1.8:8000/ws');
            // ws.value=new WebSocket('ws://localhost:8000/ws');
            ws.value.onopen=()=>{
                sendFrame();
            }
            ws.value.onmessage=(event)=>{
                const data=JSON.parse(event.data);
                // console.log(data)
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
        // audioWs.value = new WebSocket(`ws://192.168.1.16:8000/ws/transcribe_test${queryString}`);
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
                    // const currentTime = new Date().toISOString();
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
                    msgTmp.speaker=resJson.speaker;
                    msgTmp.content=resJson.data;
                    msgTmp.currentTime=currentTime;
                    msgTmp.meetingDuration=meetingDuration;


                    console.log(msgTmp)
                    cnt.value+=1;
                    records.value.push(
                        {
                            'index':cnt.value,
                            'speaker':resJson.speaker,
                            'content':resJson.data,
                            'currentTime':currentTime,
                            'meetingDuration':meetingDuration
                        }
                    )



                    // console.log(resJson.speaker,":",resJson.data)
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
        //.meetingVideo{
        //    width: 100%;
        //    height: 100%;
        //}

        .meetingVideo {
            width: 80%; /* 盒子宽度 */
            height: 80%; /* 盒子高度 */
            background: #F0F8FF; /* 背景颜色：浅蓝色，与整体设计搭配 */
            border-radius: 15px; /* 圆角，增加美观 */
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2); /* 阴影，增加层次感 */
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden; /* 防止视频超出盒子 */
            position: relative; /* 为视频添加遮罩层做准备 */

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(30, 144, 255, 0.1); /* 浅蓝色遮罩层，增加视觉效果 */
                pointer-events: none; /* 不影响交互 */
            }

            video {
                width: 100%;
                height: 100%;
                object-fit: cover; /* 视频内容覆盖整个盒子 */
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
                background: #F0F8FF; /* 浅蓝色背景 */
                color: #333;
            }

            .generate-button {
                margin-top: 3px;
                padding: 10px 20px;
                background: #1E90FF; /* 蓝色按钮 */
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;

                &:hover {
                    background: #007BFF; /* 鼠标悬停时的颜色 */
                }
            }
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
                .faceInfo{
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }

                .generateReport{
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }

                .savaData{
                    margin-left: 0px;
                    margin-top: 10px;
                    width: 100%;
                    height: 50px;
                }

                //.downLoadReport{
                //    margin-left: 0px;
                //    margin-top: 10px;
                //    width: 100%;
                //    height: 50px;
                //}
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