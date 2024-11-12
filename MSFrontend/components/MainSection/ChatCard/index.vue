<script setup>
// 可以在此处定义一些数据和方法
// 使用 defineProps 定义 props
const props = defineProps({
    result: {
        type: String,
        required: true
    }
});
</script>

<template>
    <div class="flex  p-4  rounded-lg  w-full ">
        <!-- 用户头像 -->
        <div class="flex-shrink-0">
            <Avatar>
                <AvatarImage src="https://github.com/radix-vue.png" alt="@radix-vue" />
                <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <!-- 用户名 -->
            <div class="flex items-center">
                <span class="font-semibold text-slate-500">User 1</span>
            </div>
        </div>

        <!-- 对话内容 -->
        <div class="ml-4 flex flex-col flex-grow">

            <!-- 消息内容 -->
            <p class="mt-2 text-black text-start ">
                {{ props.result }}
            </p>

            <!-- 时间显示 -->
            <div class="ml-4 flex flex-col items-end justify-between text-gray-700 text-sm">
                <span>5:01 - 5:20</span>
            </div>
        </div>

    </div>
</template>

<style scoped>
/* 添加一些额外的样式 */
</style>