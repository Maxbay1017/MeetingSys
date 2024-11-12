<script setup lang="ts">

const route = useRoute();

// console.log("Current route name:", route.name);
// console.log("Current route path:", route.path);
// Computed property to check if the current route is not "home"
const showPeopleSection = computed(() => route.name !== 'home');
</script>

<template>
    <!-- <div>
        <p>{{ route.name }}</p>
        <p>{{ route.path }}</p>
    </div> -->
    <div class="h-full w-full bg-gray-100 flex flex-col border-r justify-between">
        <!-- 历史记录区 -->
        <div class="flex-grow p-4 border-b-2 ">
            <h2 class="text-lg font-bold mb-4">历史记录</h2>
            <!-- 历史记录列表 -->
            <div class="space-y-2">
                <div class="p-2 bg-white rounded shadow-sm flex items-center">
                    <span>会议纪要 01</span>
                    <span class="ml-auto text-gray-500">11月25日</span>
                </div>
                <div class="p-2 bg-white rounded shadow-sm flex items-center">
                    <span>会议纪要 02</span>
                    <span class="ml-auto text-gray-500">11月25日</span>
                </div>
                <!-- 添加更多记录时可以继续此结构 -->
            </div>
        </div>

        <!-- 人员区 -->
        <div v-if="showPeopleSection" class="p-4 space-y-2">
            <!-- 每个用户项 -->
            <div class="flex items-center p-2 bg-white rounded shadow-sm">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex-shrink-0"></div>
                <span class="ml-2">User 1</span>
            </div>
            <div class="flex items-center p-2 bg-white rounded shadow-sm">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex-shrink-0"></div>
                <span class="ml-2">User 2</span>
            </div>
            <div class="flex items-center p-2 bg-white rounded shadow-sm">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex-shrink-0"></div>
                <span class="ml-2">User 3</span>
            </div>
            <!-- 可以根据需求继续添加用户项 -->
        </div>
    </div>
</template>

<style lang="scss"></style>