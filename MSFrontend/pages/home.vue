<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { useRouter } from 'vue-router'
const router = useRouter()

// 表单数据
const meetingTitle = ref('')        // 会议标题
const meetingParticipants = ref('2') // 参会人数
const meetingTime = ref('')          // 会议时间
const meetingNotes = ref('')         // 会议备注
const isFinish = ref(false)          // 添加信息是否成功

// 动态生成卡片数量
const participants = ref<{ name: string; status: string }[]>([]) // 指定类型

// 浮层状态和当前选中的卡片
const showOverlay = ref(false)     // 记录浮层打开状态 fasle关闭 true打开
const selectedCardIndex = ref<number | null>(null) // 记录当前打开的浮层 对应的卡片index

// 浮层卡片中的参会人员信息
const participantName = ref('') // 记录参会人员姓名
const audioChunks: Blob[] = [] // 用于存储录音数据的数组
const isRecording = ref(false)  // 记录是否在录音
let mediaRecorder: MediaRecorder | null = null //录音器

// 点击“Next”按钮后生成卡片
const handleNextClick = () => {
    isFinish.value = true
    // 重新生成 participants 数组
    participants.value = Array.from({ length: parseInt(meetingParticipants.value) || 0 }, () => ({
        name: '',
        status: '未添加'
    }))
}

// 处理卡片点击事件
const handleCardClick = (index: number) => {
    selectedCardIndex.value = index
    showOverlay.value = true
}

// 开始录音
const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        mediaRecorder = new MediaRecorder(stream)
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data)
        }
        mediaRecorder.start()
        isRecording.value = true
    }).catch(error => console.error("录音失败:", error))
}

// 停止录音并获取音频数据
const stopRecording = () => {
    if (mediaRecorder) {
        mediaRecorder.stop()
        isRecording.value = false
    }
}

const sendData = async () => {
    stopRecording();

    // 获取音频Blob数据
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

    // 创建FormData对象以便发送音频数据和姓名
    const formData = new FormData();
    formData.append('name', participantName.value);
    formData.append('audio', audioBlob, 'recording.wav');

    try {
        const response = await fetch('http://localhost:27000/api/saveAudio', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            console.log('数据发送成功');
            // 更新参会人员信息
            if (selectedCardIndex.value !== null) {
                participants.value[selectedCardIndex.value] = {
                    name: participantName.value,
                    status: '添加成功'
                };
            }
        } else {
            console.error('数据发送失败');
        }
    } catch (error) {
        console.error('网络错误:', error);
    }

    // 关闭浮层并清空数据
    closeOverlay();
};


// 关闭浮层
const closeOverlay = () => {
    showOverlay.value = false
    selectedCardIndex.value = null
    participantName.value = '' //清空浮层人员姓名
    audioChunks.length = 0     //初始化语音长度
}

// 是否可以开始会议的计算属性
const canStartMeeting = computed(() => {
    return participants.value.every(participant => participant.status === '添加成功');
});

watch(
    participants,
    (newVal) => {
        console.log('participants 发生了变化:', newVal);
        // 执行逻辑
    },
    { deep: true }
);

const goToIndexPage = () => {
    router.push('/') // 导航到 index 页面（假设 index 页面路径为 '/'）
}

</script>

<template>
    <!-- 表单区 -->
    <div v-if="!isFinish" class="flex items-center justify-center">
        <div class="InitMeetingSection w-[80%] h-screen my-52">
            <Card class="w-full h-1/2">
                <CardHeader>
                    <CardTitle>初始化会议</CardTitle>
                    <CardDescription>请添加相关会议信息!</CardDescription>
                </CardHeader>
                <CardContent>
                    <form>
                        <div class="grid items-center w-full gap-4">
                            <div class="flex flex-col space-y-1.5">
                                <Label for="name">会议标题</Label>
                                <Input id="name" placeholder="您的会议标题: 第一次会议" v-model="meetingTitle" />
                            </div>
                            <div class="flex flex-col space-y-1.5">
                                <Label for="framework">会议人数</Label>
                                <Select v-model="meetingParticipants">
                                    <SelectTrigger id="framework">
                                        <SelectValue placeholder="选择会议人数" />
                                    </SelectTrigger>
                                    <SelectContent position="popper">
                                        <SelectItem value="2">2</SelectItem>
                                        <SelectItem value="3">3</SelectItem>
                                        <SelectItem value="4">4</SelectItem>
                                        <SelectItem value="5">5</SelectItem>
                                        <SelectItem value="6">6</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div class="flex flex-col space-y-1.5">
                                <Label for="meetingTime">会议时间</Label>
                                <Input id="meetingTime" placeholder="请输入会议时间" v-model="meetingTime" />
                            </div>
                            <div class="flex flex-col space-y-1.5">
                                <Label for="meetingNotes">会议备注</Label>
                                <Input class="h-32" id="meetingNotes" placeholder="添加您的会议备注" v-model="meetingNotes" />
                            </div>
                        </div>
                    </form>
                </CardContent>
                <CardFooter class="flex justify-end px-6 pb-6">
                    <Button @click="handleNextClick">Next</Button>
                </CardFooter>
            </Card>
        </div>
    </div>

    <!-- 动态生成的卡片 -->
    <div v-else class="p-4">
        <div class="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            <Card v-for="(participant, index) in participants" :key="index"
                class="bg-white shadow-md rounded-lg p-4 cursor-pointer" @click="handleCardClick(index)">
                <CardHeader>
                    <CardTitle class="text-2xl"> {{ participant.name || `参会人员 ${index + 1}` }}</CardTitle>
                    <CardDescription>{{ participant.status }}</CardDescription>
                </CardHeader>
                <CardContent>
                    <p v-if="participant.status === '添加成功'" class="text-teal-600">声纹识别成功!</p>
                    <p v-else></p>
                </CardContent>
            </Card>
        </div>
    </div>

    <!-- 浮层 -->
    <div v-if="selectedCardIndex !== null && showOverlay"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 class="text-xl font-bold mb-4">添加会议人员</h2>
            <div class="flex flex-col space-y-1.5 mb-2">
                <Label for="name">参会人员姓名:</Label>
                <Input v-model="participantName" id="name" placeholder="您的名字" />
            </div>
            <div class="flex flex-col space-y-1.5 mb-2">
                <Label for="voice">请使用麦克风录入一段语音</Label>
                <div class="flex space-y-1.5">
                    <!-- 录音按钮 -->
                    <button @click="isRecording ? stopRecording() : startRecording()"
                        class="flex items-center justify-center w-10 h-10 bg-gray-200 rounded-full">
                        <span v-if="!isRecording">▶️</span>
                        <span v-else>⏸️</span>
                    </button>
                    <!-- 音频波形展示区域 -->
                    <div class="flex-grow mx-4 border-gray-300 relative">
                        <div class="absolute inset-0 flex items-center">
                            <div class="h-4 bg-gray-400 w-full rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="flex justify-between">
                <Button class="mt-4" @click="closeOverlay">关闭</Button>
                <Button class="mt-4" @click="sendData">确认</Button>
            </div>
        </div>
    </div>

    <div v-if="isFinish && canStartMeeting"
        class="fixed bottom-1 left-1/2 transform -translate-x-1/2 flex justify-center items-center  w-full h-20 bg-neutral-200 rounded-lg">
        <Button @click="goToIndexPage" class="h-full text-3xl p-6 text-neutral-200 bg-[#358A55]">开始会议</Button>
    </div>

</template>

<style scoped>
/* 可选样式 */
</style>
