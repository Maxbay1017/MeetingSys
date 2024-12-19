<template>
  <div class="flex flex-col ">
    <Top/>

    <div class="flex mt-20 mx-auto max-w-7xl w-full px-4">
      <router-view></router-view>
    </div>

    <!-- <MeetingBottom/> -->
  </div>


</template>

<script setup lang="ts" name="app">
  // import home from '@/views/home/index.vue';
  // import Test from '@/views/Test/index.vue';

</script>

<style scoped lang="scss">
</style>
