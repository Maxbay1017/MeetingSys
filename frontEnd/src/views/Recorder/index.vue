<script setup lang="ts" name="Recorder">
import { ref, computed } from 'vue'

const speakerName = ref('')
const isRecording = ref(false)
const audioBlob = ref<Blob | null>(null)

const canSubmit = computed(() => {
    return speakerName.value.trim() && audioBlob.value
})

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

async function toggleRecording() {
    if (!isRecording.value) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaRecorder = new MediaRecorder(stream)

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data)
            }

            mediaRecorder.onstop = () => {
                audioBlob.value = new Blob(audioChunks, { type: 'audio/wav' })
                audioChunks = []
                stream.getTracks().forEach(track => track.stop())
            }

            mediaRecorder.start()
            isRecording.value = true
        } catch (error) {
            console.error('无法访问麦克风:', error)
            alert('无法访问麦克风，请检查权限设置')
        }
    } else {
        mediaRecorder?.stop()
        isRecording.value = false
    }
}

async function submitRecording() {
    if (!canSubmit.value) return

    const formData = new FormData()
    formData.append('name', speakerName.value)
    formData.append('audio', audioBlob.value!, `${speakerName.value}.wav`)

    try {
        const response = await fetch('http://192.168.1.8:8000/api/upload', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        console.log('提交成功:', result)
        alert('录音提交成功！')

        // 重置表单
        speakerName.value = ''
        audioBlob.value = null
        isRecording.value = false
    } catch (error) {
        console.error('提交失败:', error)
        alert('提交失败，请稍后重试')
    }
}
</script>

<template>
    <div class="p-4">
        <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden">
            <div class="p-6">
                <h2 class="text-xl font-semibold mb-4">录音信息录入</h2>

                <!-- 录音者姓名输入 -->
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">录音者姓名</label>
                    <input
                        v-model="speakerName"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="请输入录音者姓名"
                    />
                </div>

                <!-- 录音控制 -->
                <div class="mb-4">
                    <button
                        @click="toggleRecording"
                        :class="{
                            'bg-red-500 hover:bg-red-600': isRecording,
                            'bg-blue-500 hover:bg-blue-600': !isRecording
                        }"
                        class="w-full text-white font-medium py-2 px-4 rounded-md transition-colors"
                    >
                        {{ isRecording ? '停止录音' : '开始录音' }}
                    </button>
                </div>

                <!-- 提交按钮 -->
                <button
                    @click="submitRecording"
                    :disabled="!canSubmit"
                    class="w-full bg-green-500 text-white font-medium py-2 px-4 rounded-md hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                    提交录音
                </button>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
</style>