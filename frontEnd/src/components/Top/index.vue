<template>
    <div id="TopNav" class="fixed z-30 flex items-center w-full h-16 bg-white border-b">
        <div id="NavSection" class="flex items-center justify-between w-full h-full px-6 mx-auto max-w-[1150px]">
            
            <div id="logo" class="flex items-center justify-center px-6 py-4 gap-x-2">
                <img src="@/assets/ltd.jpg" class="w-[32px] rounded-full">
                <span class="font-semibold text-lg text-gray-700">链天地会议系统</span>
            </div>

            <div class="hidden md:flex items-center bg-[#F1F1F2] p-1 rounded-full max-w-[380px] w-full">
                <input type="text" placeholder="Search contents" class="w-full pl-3 bg-transparent placeholder-[#838383] text-[15px] focus:outline-none" />
                <div class="px-3 py-1 flex items-center border-l border-l-gray-300">
                    <Icon icon="ri:search-line" />
                </div>
            </div>

            <div id="history" class="flex items-center justify-center gap-3 min-w-[275px] max-w-[320px] w-full">
                <button @click="showMenu = !showMenu" class="flex items-center border rounded-sm px-3 py-[6px] hover:bg-gray-100">
                    <Icon icon="si:align-right-line"/>
                    <span class="px-3 font-medium text-[15px] border-l">历史记录</span>
                </button>
            </div>

            <div v-if="showMenu" class="absolute top-[65px] right-0 w-[400px] h-[750px] bg-white border rounded-lg shadow-lg px-4 py-6 flex flex-col gap-y-4">
                <div class="w-full overflow-y-auto flex flex-col gap-y-4">
                    <div v-for="(meeting, index) in meetingHistory" :key="index" class="bg-white rounded-lg shadow-md p-4 mb-4">
                        <h2 class="text-lg font-semibold text-gray-800 mb-2">会议名称: {{ meeting.name }}</h2>
                        <p class="text-sm text-gray-500">时间: {{ meeting.time }}</p>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script setup lang="ts" name="TopNav">
import { Icon } from "@iconify/vue";
import { ref } from "vue";

let showMenu = ref(false);

// 生成一个数组，包含 6 条会议信息
const meetingHistory = ref([
  { name: "项目启动会议", time: "2024年4月20日 10:00 AM" },
  { name: "周度进度会议", time: "2024年4月22日 2:00 PM" },
  { name: "技术分享会", time: "2024年4月25日 4:00 PM" },
  { name: "季度总结会议", time: "2024年4月28日 3:00 PM" },
  { name: "需求评审会议", time: "2024年5月2日 9:00 AM" },
  { name: "问题反馈会议", time: "2024年5月5日 11:00 AM" },
]);
</script>
