<script setup>
import { Button } from '@/components/ui/button'
import { ChevronRightIcon } from '@radix-icons/vue'

// 引用全局的 transcriptionResult 状态
const transcriptionResult = useState('transcriptionResult');
const transcriptionSpeaker =useState('transcriptionSpeaker');

// watchEffect(() => {
//     console.log(`OldValue changed to ${transcriptionResult}, NewValue is now ${transcriptionResult}`)
//     console.log(typeof transcriptionResult.value)
// })

// step1: 定义一个数组，用于存储每次更新的 transcriptionResult 值
const transcriptionHistory = ref([{}]);


// step2: 监听 transcriptionResult 的变化，每次更新时将值添加到 transcriptionHistory 数组中
watchEffect(() => {
    if (transcriptionResult.value||transcriptionSpeaker.value) {
        transcriptionHistory.value.push({transcriptionResult,transcriptionSpeaker});
    }
});

</script>

<template>
    <div class="flex flex-col gap-4 h-full bg-white items-center justify-between overflow-y-hidden max-h-[100vh]">
        <div
            class="RecordSection w-full flex flex-col  rounded-lg p-2 items-center justify-between overflow-y-scroll max-h-[90vh]">
            <div class="ChatCard flex flex-col w-3/4 ">
                <!-- step2: 遍历 transcriptionHistory 数组并显示每个值
                <p v-for="(result, index) in transcriptionHistory" :key="index">{{ result }}</p> -->
                <!-- 遍历 transcriptionHistory 数组，每个值传给 MainSectionChatCard 组件 -->
                <MainSectionChatCard v-for="(result, index) in transcriptionHistory" :key="index" :result="result" />
            </div>
        </div>
        <div class="AudioSection w-3/4 h-30 rounded-lg flex p-2 justify-center gap-2">
            <!-- 录音进度条 -->
            <MainSectionAudioRecorder />
            <!-- 会议结束按钮 -->
            <Button class="MeetingEndButton w-40 h-full" variant="outline" size="icon">
                <ChevronRightIcon class="w-8 h-8" />
                <p>会议结束</p>
            </Button>
        </div>
    </div>
</template>

<style lang="scss"></style>