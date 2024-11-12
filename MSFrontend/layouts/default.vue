<template>
    <div class="grid grid-cols-5 h-screen">
        <!-- <Sidebar /> -->
        <!-- 左侧 SlideBar 占 1/5 宽度 -->
        <div class="col-span-1 bg-gray-200 ">
            <SlideBar />
        </div>
        <!-- 右侧 MainSection 占 4/5 宽度 -->
        <div class="col-span-4 bg-white ">
            <slot />
        </div>
    </div>
</template>