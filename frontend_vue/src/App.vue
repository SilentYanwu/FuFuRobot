<script setup lang="ts">
import Sidebar from '@/components/Sidebar/Sidebar.vue'
import ChatArea from '@/components/Chat/ChatArea.vue'
import CursorEffect from './components/Effects/CursorEffect.vue'
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center p-5 relative"
    style="
      background-image: url('/src/assets/images/bg.png');
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
    "
  >
    <div class="fixed top-0 left-0 w-full h-full bg-black/30 -z-10"></div>
    <div class="app-container">
      <Sidebar />
      <ChatArea />
    </div>
  </div>
  <CursorEffect />
</template>

<style>
.app-container {
  display: flex;
  width: 100%;
  max-width: 1400px;
  height: 90vh;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}
</style>
