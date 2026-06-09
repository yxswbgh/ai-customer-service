<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <el-menu
        :default-active="route.path"
        mode="horizontal"
        router
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/chat">对话</el-menu-item>
        <el-menu-item index="/knowledge">知识库</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style>
.app-container {
  min-height: 100vh;
}
.app-header {
  padding: 0;
}
</style>
