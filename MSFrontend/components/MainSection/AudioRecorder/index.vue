<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

//获取browser media权限
// navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;

let ws = null;
let record = null;
let timeInte = null;

const isPlaying = ref(false);
const currentTime = ref(0); // 以秒为单位存储时间
// const transcriptionResult = ref(''); // 声明一个响应式变量来存储 WebSocket 返回的数据
// 声明一个全局的 transcriptionResult 状态
const transcriptionResult = useState('transcriptionResult', () => ''); // 初始值为空字符串
const transcriptionSpeaker = useState('transcriptionSpeaker', () => ''); // 初始值为空字符串
let timer = null;

// interface TranscriptionResult {
//     code: number;
//     info: string;  // 如果 `info` 是 JSON 字符串，可以保持为 `string` 类型，后续需要解析时可以用 `JSON.parse`
//     data: string;
// }

// const transcriptionResult = useState < TranscriptionResult > ('transcriptionResult', () => ({
//     code: 0,
//     info: '',
//     data: ''
// }));

// 切换播放状态
const togglePlay = () => {
    isPlaying.value = !isPlaying.value;
    if (isPlaying.value) {
        startRecording(); //录音函数
        startTimer();
    } else {
        stopTimer();
        stopRecording(); //停止录音函数
    }
};

// 开始计时
const startTimer = () => {
    if (!timer) {
        timer = setInterval(() => {
            currentTime.value++;
        }, 1000);
    }
};

// 停止计时
const stopTimer = () => {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
};

// 格式化时间为 mm:ss
const formattedTime = computed(() => {
    const minutes = Math.floor(currentTime.value / 60).toString().padStart(2, '0');
    const seconds = (currentTime.value % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
});


function startRecording() {
    console.log('Start Recording');
    // var speakerVerificationCheckbox = document.getElementById('speakerVerification');
    // var sv = speakerVerificationCheckbox.checked ? 1 : 0;
    var sv = 1
    // var lang = document.getElementById("lang").value
    var lang = 'zh'
    // Construct the query parameters
    var queryParams = [];
    if (lang) {
        queryParams.push(`lang=${lang}`);
    }
    if (sv) {
        queryParams.push('sv=1');
    }
    var queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';

    ws = new WebSocket(`ws://localhost:27000/ws/transcribe_test${queryString}`);
    ws.binaryType = 'arraybuffer';

    ws.onopen = function (event) {
        console.log('WebSocket connection established');
        record.start();
        timeInte = setInterval(function () {
            if (ws.readyState === 1) {
                var audioBlob = record.getBlob();
                // console.log('Blob size: ', audioBlob.size);

                // Read the Blob content for debugging
                var reader = new FileReader();
                reader.onloadend = function () {
                    // console.log('Blob content: ', new Uint8Array(reader.result));
                    ws.send(audioBlob);
                    console.log('Sending audio data');
                    record.clear();
                };
                reader.readAsArrayBuffer(audioBlob);      //  FileReader 完成对 audioBlob 的读取后，无论成功或失败，都会触发 onloadend
            }
        }, 500);
    };

    ws.onmessage = function (evt) {
        console.log('Received message: ' + evt.data);
        try {
            let resJson = JSON.parse(evt.data)
            console.log('Received message&Jsonfiy: ' + resJson);
            if (resJson.code == 0) {
                // var jsonResponse = JSON.stringify(resJson, null, 4);
                // transcriptionResult.value += "\n" + (resJson.data || 'No speech recognized');
                transcriptionResult.value = resJson.data || { message: 'No speech recognized' };
                transcriptionSpeaker.value=resJson.speaker || { message: 'No speech recognized' };
            }
            // if (resJson.code == 2) {
            //     transcriptionSpeaker.value = resJson.data || { message: 'No speaker recognized' }
            // }
        } catch (e) {
            console.error('Failed to parse response data', e);
            // transcriptionResult.value += "\n" + evt.data;
            transcriptionResult.value = evt.data;
        }
    };

    ws.onclose = function () {
        console.log('WebSocket connection closed');
    };

    ws.onerror = function (error) {
        console.error('WebSocket error: ' + error);
    };

    // recordButton.textContent = "Stop Recording";
    // recordButton.classList.add("recording");
    // isRecording = true;
    isPlaying = true;
}

function stopRecording() {
    console.log('Stop Recording');
    if (ws) {
        ws.close();
        record.stop();
        clearInterval(timeInte);
    }
    // recordButton.textContent = "Start Recording";
    // recordButton.classList.remove("recording");
    // isRecording = false;
    isPlaying = false;
}


function init(rec) {
    record = rec;
}


var Recorder = function (stream) {
    var sampleBits = 16; // Sample bits 采样位数，这里是 16 位（即每个样本用 16 位表示）。
    var inputSampleRate = 48000; // Input sample rate 输入采样率，默认是 48000 Hz
    var outputSampleRate = 16000; // Output sample rate 输出采样率，默认是 16000 Hz（通常用于 ASR 模型）    
    var channelCount = 1; // Single channel
    var context = new AudioContext(); //处理和分析音频数据
    var audioInput = context.createMediaStreamSource(stream);  //  context.createMediaStreamSource(stream) 将 MediaStream 转换为音频源。
    var recorder = context.createScriptProcessor(4096, channelCount, channelCount); // 用于实时处理音频数据，这里设置每次处理 4096 个样本，单声道输入和输出。
    var audioData = { // 存储音频数据并处理采样
        size: 0,
        buffer: [], // 存储音频缓冲数据。
        inputSampleRate: inputSampleRate,
        inputSampleBits: sampleBits, // 记录输入的采样率和位深。
        clear: function () {     // 清除缓冲区
            this.buffer = [];
            this.size = 0;
        },
        input: function (data) { // 将新录制的数据推入 buffer
            this.buffer.push(new Float32Array(data));
            this.size += data.length;
        },
        encodePCM: function () {   // 将缓冲的音频数据编码为 PCM 格式的 Blob 对象，以便可以传输或保存。
            var bytes = new Float32Array(this.size);
            var offset = 0;
            for (var i = 0; i < this.buffer.length; i++) {
                bytes.set(this.buffer[i], offset);
                offset += this.buffer[i].length;
            }
            var dataLength = bytes.length * (sampleBits / 8);
            var buffer = new ArrayBuffer(dataLength);
            var data = new DataView(buffer);
            offset = 0;
            for (var i = 0; i < bytes.length; i++, offset += 2) {
                var s = Math.max(-1, Math.min(1, bytes[i]));
                data.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            }
            return new Blob([data], { type: 'audio/pcm' });
        }
    };

    this.start = function () { // 始录音，连接音频源和处理节点。
        audioInput.connect(recorder);
        recorder.connect(context.destination);
    };

    this.stop = function () {
        recorder.disconnect(); // 停止录音，断开连接。
    };

    this.getBlob = function () {
        return audioData.encodePCM(); // 获取编码后的音频 Blob。
    };

    this.clear = function () {
        audioData.clear(); // 清除缓冲区数据。
    };

    function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {  // 将输入音频从 inputSampleRate 采样率下采样到 outputSampleRate。
        if (outputSampleRate === inputSampleRate) {
            return buffer;
        }
        var sampleRateRatio = inputSampleRate / outputSampleRate;
        var newLength = Math.round(buffer.length / sampleRateRatio);
        var result = new Float32Array(newLength);
        var offsetResult = 0;
        var offsetBuffer = 0;
        while (offsetResult < result.length) {
            var nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
            var accum = 0, count = 0;
            for (var i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
                accum += buffer[i];
                count++;
            }
            result[offsetResult] = accum / count;
            offsetResult++;
            offsetBuffer = nextOffsetBuffer;
        }
        return result;
    }

    recorder.onaudioprocess = function (e) { // 音频数据块准备好时，onaudioprocess 回调被触发
        console.log('onaudioprocess called');
        var resampledData = downsampleBuffer(e.inputBuffer.getChannelData(0), inputSampleRate, outputSampleRate);
        audioData.input(resampledData); // 处理的每个音频块先被下采样到目标采样率，然后存入 audioData 的 buffer
    };
};


// 在 onMounted 中检查客户端环境
onMounted(() => {
    if (process.client && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then((mediaStream) => {
                init(new Recorder(mediaStream));
            })
            .catch((error) => {
                console.log('Error accessing media devices.', error);
            });
    } else {
        console.warn('navigator.mediaDevices.getUserMedia is not available');
    }
});

// 组件销毁时清除计时器
onUnmounted(() => {
    stopTimer();
});
</script>


<template>
    <div class="flex items-center p-4 bg-gray-100 rounded-lg shadow-md w-full">

        <!-- 播放按钮 -->
        <button @click="togglePlay" class="flex items-center justify-center w-10 h-10 bg-gray-200 rounded-full">
            <span v-if="!isPlaying">▶️</span>
            <span v-else><img src="/assets/icons/material-symbols--pause.svg" /></span>
        </button>

        <!-- 音频波形展示区域 -->
        <div class="flex-grow mx-4 border-t border-gray-300 relative">
            <div class="absolute inset-0 flex items-center">
                <!-- 模拟的音频波形，可以根据实际需求替换为动态波形 -->
                <div class="h-4 bg-gray-400 w-full rounded"></div>
            </div>
        </div>

        <!-- 录音时长显示 -->
        <div class="text-gray-700 font-semibold">{{ formattedTime }}</div>
    </div>
</template>

<style scoped>
/* 你可以在这里定义额外的样式 */
</style>