<template>
  <div class="top">
      <div class="logo">
          <img src="../../assets/ltd.jpg" alt="Icon" class="icon" />
          <div class="title">
              <h1>LTD本地视频会议系统</h1>
          </div>
      </div>

  </div>
</template>

<script setup lang="ts" name="Top">

</script>



<style scoped lang="scss">
  .top {
      height: 70px;
      width: 100%;
      background: linear-gradient(90deg, #1E90FF, #00BFFF);
      display: flex;
      align-items: center;
      padding: 0 20px;
      color: white;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);

      .logo {
          display: flex;
          align-items: center;
          margin-right: 20px; /* 图标与文字之间的间距 */

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
  }

</style>