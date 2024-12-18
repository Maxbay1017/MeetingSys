import { createApp } from 'vue'
//清除默认样式
import '@/input.css'
import '@/style/reset.scss'
//引入根组件APP
// @ts-ignore
import App from './App.vue'

//引入全局组件
// @ts-ignore
import Top from '@/components/Top/index.vue';
// @ts-ignore
import MeetingBottom from '@/components/MeetingBottom/index.vue';


//引入vue-rouer
import router from "@/router";
import pinia from '/store';

//引入 element-plus 插件
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
//@ts-ignore
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'



const app=createApp(App)
//top组件
app.component('Top',Top);
app.component('MeetingBottom',MeetingBottom);
//安装 element-plus 插件
app.use(ElementPlus, {
    locale: zhCn
})
app.use(router);
app.mount('#app')

