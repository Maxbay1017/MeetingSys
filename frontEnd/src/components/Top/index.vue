<template>
    <div class="top">
        <div class="logo">
            <img src="../../assets/ltd.jpg" alt="Icon" class="icon" />
            <div class="title">
                <h1>LTD本地视频会议系统</h1>
            </div>
        </div>

        <!-- 右侧下拉框 -->
        <div class="dropdown">
            <el-dropdown @command="handleCommand">
        <span class="el-dropdown-link" style="justify-content: center;align-items: center">
          <h style="margin-right: 5px;font-size: 20px">菜单</h>
          <el-icon :size="30" style="vertical-align: middle;">
            <Menu />
          </el-icon>
        </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="recorder">录音界面</el-dropdown-item>
                        <el-dropdown-item command="history">历史记录</el-dropdown-item>
                        <el-dropdown-item command="search">搜索</el-dropdown-item>
                        <el-dropdown-item command="Home">会议界面</el-dropdown-item>
                        <el-dropdown-item command="Upload">上传历史会议</el-dropdown-item>
                        <el-dropdown-item command="BlinkStatistics">眨眼区间搜索</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
</template>

<script setup lang="ts" name="Top">
    import { useRouter } from 'vue-router';
    import { Menu } from '@element-plus/icons-vue';
    const router = useRouter();
    const handleCommand = (command: string) => {
        if (command === 'history') {
            router.push({ path: '/History' });
        } else if (command === 'search') {
            router.push({ path: '/Search' });
        }else if(command==='Home'){
            router.push({ path: '/Test' });
        }else if(command==='recorder'){
            router.push({path:'/Recorder'});
        }else if(command==='Upload'){
            router.push({path:'/UploadVideo2'});
        }else if(command==='BlinkStatistics'){
            router.push({path:'/BlinkStatistics'});
        }
    }
</script>

<style scoped lang="scss">
.top {
    height: 70px;
    width: 100vw;
    background: linear-gradient(90deg, #1e90ff, #00bfff);
    display: flex;
    align-items: center;
    justify-content: space-between; /* 左右布局 */
    padding: 0 20px;
    color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);

    .logo {
        display: flex;
        align-items: center;

        .icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
    }

    .title {
        margin-left: 10px;
        h1 {
            font-size: 20px;
            margin: 0;
            font-weight: bold;
        }

        p {
            font-size: 14px;
            margin: 0;
            opacity: 0.8;
        }
    }

    .dropdown {
        .el-dropdown-link {
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
        }
    }
}
</style>