<template>
  <div class="buttom">
      <p class="copyright">© 2024 LTD本地视频会议系统 </p>
  </div>
</template>

<script setup lang="ts" name="MeetingButtom">

</script>

<style scoped lang="scss">
  //.buttom{
  //  width: 100%;
  //  height: 70px;
  //  background: #7f7f7f;
  //}
  .buttom {
      width: 100vw;
      height: 70px;
      background: linear-gradient(90deg, #00BFFF, #1E90FF);
      display: flex;
      justify-content: center;
      align-items: center;
      color: white;
      font-size: 14px;
      box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);

      .copyright {
          margin: 0;
          opacity: 0.8;
      }
  }
</style>