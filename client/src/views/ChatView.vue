<template>
  <div class="chat">
    <h1>对话</h1>
    <p v-if="sessionId">会话 ID: {{ sessionId }}</p>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const sessionId = route.params.sessionId  // 有则显示，无则是新对话
</script>
