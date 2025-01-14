import {createRouter,createWebHistory} from "vue-router";
export default createRouter({
    history:createWebHistory(),
    routes:
        [
            {
                path:'/Home',
                component:()=>import('@/views/home/index.vue'),
            },
            {
                path:'/Test',
                component:()=>import('@/views/Test/index.vue')
            },
            {
            path:'/Test2',
            component:()=>import('@/views/Test2/index.vue')
            },
            {
                path:'/Recorder',
                component:()=>import('@/views/Recorder/index.vue')
            },
            {
                path:'/Recorder2',
                component:()=>import('@/views/Recorder2/index.vue')
            },
            {
                path:'/Search',
                component:()=>import('@/views/Search/index.vue')
            },
            {
                path:'/History',
                component:()=>import('@/views/History/index.vue')
            },
            {
                path:'/Recorder',
                component:()=>import('@/views/Recorder/index.vue')
            },
            {
                path:'/',
                component:()=>import('@/views/init/index.vue')
            },
            {
                path:'/UploadVideo2',
                component:()=>import('@/views/uploadVideo/index.vue')
            },
            {
                path:'/BlinkStatistics',
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