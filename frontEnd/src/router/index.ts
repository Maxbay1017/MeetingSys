import {createRouter,createWebHistory} from "vue-router";

export default createRouter({
    history:createWebHistory(),
    routes:
        [
            {
                path:'/Home',
                // @ts-ignore
                component:()=>import('@/views/home/index.vue'),
            },
            {
                path:'/Test',
                // @ts-ignore
                component:()=>import('@/views/Test/index.vue')
            },
            {
                 path:'/Test2',
                // @ts-ignore
                component:()=>import('@/views/Test2/index.vue')
            },
            {
                path:'/Recorder',
                // @ts-ignore
                component:()=>import('@/views/Recorder/index.vue')
            },
            {
                path:'/Recorder2',
                // @ts-ignore
                component:()=>import('@/views/Recorder2/index.vue')
            },
            {
                path:'/Search',
                // @ts-ignore
                component:()=>import('@/views/Search/index.vue')
            },
            {
                path:'/History',
                // @ts-ignore
                component:()=>import('@/views/History/index.vue')
            },
            {
                path:'/Recorder',
                // @ts-ignore
                component:()=>import('@/views/Recorder/index.vue')
            },
            {
                path:'/',
                // @ts-ignore
                component:()=>import('@/views/init/index.vue')
            },
            {
                path:'/UploadVideo2',
                // @ts-ignore
                component:()=>import('@/views/uploadVideo/index.vue')
            },
            {
                path:'/BlinkStatistics',
                // @ts-ignore
                component:()=>import('@/views/blinkStatistics/index.vue')
            }


    ],
    //滚动行为：控制滚动条的位置
    //切换路由时，页面跳转到最上方
    scrollBehavior() {
        return {
            left: 0,
            top: 0
        }
    }
})