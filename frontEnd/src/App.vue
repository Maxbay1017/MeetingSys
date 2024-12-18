<template>
  <div class="container">
    <Top/>

    <div class="content">
      <router-view></router-view>
    </div>

    <MeetingBottom/>
  </div>


</template>

<script setup lang="ts" name="app">
  import home from '@/views/home/index.vue';
  import Test from '@/views/Test/index.vue';

</script>

<style scoped lang="scss">
  .content{
    width: 100%;
    min-height: 700px;
  }

</style>
