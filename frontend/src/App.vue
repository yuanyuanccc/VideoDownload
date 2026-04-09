<template>
  <div style="min-height: 100vh; background-color: #0f0f23; color: #e5e7eb;">
    <Navbar />
    <main style="max-width: 80rem; margin: 0 auto; padding: 0 1rem;">
      <HeroSection @parsed="handleVideoParsed" />
      <VideoInfo 
        v-if="videoInfo" 
        :video-info="videoInfo" 
        @download="handleDownload" 
        :downloading="downloading" 
      />
      <PlatformGrid />
      <VipBanner />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Navbar from './components/Navbar.vue'
import HeroSection from './components/HeroSection.vue'
import VideoInfo from './components/VideoInfo.vue'
import PlatformGrid from './components/PlatformGrid.vue'
import VipBanner from './components/VipBanner.vue'

const videoInfo = ref(null)
const downloading = ref(false)

const handleVideoParsed = (info) => {
  videoInfo.value = info
}

const handleDownload = async (data) => {
  downloading.value = true
  try {
    const response = await axios.post('/api/download', {
      url: data.url,
      format_id: data.format.format_id
    }, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'video/mp4' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${videoInfo.value.title?.slice(0, 20) || 'video'}.mp4`
    document.body.appendChild(a)
    a.click()
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }, 1000)
    alert('下载完成！')
  } catch (error) {
    console.error('Download error:', error)
    alert('下载失败，请重试')
  } finally {
    downloading.value = false
  }
}
</script>