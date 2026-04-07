<template>
  <section style="padding: 2rem 0;">
    <h2 style="font-size: 1rem; font-weight: 600; text-align: center; margin-bottom: 1rem; color: #9ca3af;">支持的平台</h2>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; max-width: 48rem; margin: 0 auto;">
      <div
        v-for="platform in platforms"
        :key="platform.name"
        style="padding: 0.375rem 0.75rem; background: #1a1a2e; border-radius: 0.5rem; border: 1px solid #2a2a4a; display: flex; align-items: center; gap: 0.375rem; font-size: 0.875rem; color: #e5e7eb;"
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