<template>
  <section style="padding: 1rem 0 1.5rem;">
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 0.4rem; max-width: 36rem; margin: 0 auto;">
      <div
        v-for="platform in platforms"
        :key="platform.name"
        style="padding: 0.4rem 0.75rem; background: rgba(30,30,63,0.6); border-radius: 0.5rem; border: 1px solid rgba(58,58,92,0.5); display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: #d1d5db; transition: all 0.2s; cursor: default;"
        onmouseover="this.style.borderColor='rgba(0,212,255,0.4)';this.style.background='rgba(0,212,255,0.1)'"
        onmouseout="this.style.borderColor='rgba(58,58,92,0.5)';this.style.background='rgba(30,30,63,0.6)'"
      >
        <span>{{ platform.icon }}</span>
        <span>{{ platform.name }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
const platforms = [
  { name: 'YouTube', icon: '📺' },
  { name: 'B站', icon: '📱' },
  { name: '抖音', icon: '🎵' },
  { name: 'TikTok', icon: '🎶' },
  { name: 'Twitter', icon: '🐦' },
  { name: 'Ins', icon: '📷' },
  { name: '微博', icon: '🔥' },
  { name: '快手', icon: '🎬' },
  { name: '小红书', icon: '📕' },
]
</script>