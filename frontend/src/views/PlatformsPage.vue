<template>
  <div style="min-height: 100vh; background: linear-gradient(180deg, #0f0f23 0%, #13132a 100%); color: #e5e7eb;">
    <Navbar />
    <main style="max-width: 72rem; margin: 0 auto; padding: 0 1rem;">
      <!-- Page Header -->
      <section style="padding: 3rem 0 2rem; text-align: center;">
        <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.75rem; letter-spacing: -0.025em;">
          <span style="background: linear-gradient(135deg, #fff 0%, #00d4ff 50%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            支持平台
          </span>
        </h1>
        <p style="color: #9ca3af; font-size: 1.125rem; max-width: 500px; margin: 0 auto;">
          VideoGrab 支持从 1800+ 视频平台解析和下载视频
        </p>
      </section>

      <!-- Platform Grid -->
      <section style="padding: 1rem 0 3rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.25rem;">
          <div
            v-for="platform in platforms"
            :key="platform.name"
            style="background: linear-gradient(135deg, rgba(30,30,63,0.8) 0%, rgba(15,15,35,0.9) 100%); border-radius: 1rem; border: 1px solid rgba(58,58,92,0.6); padding: 1.5rem; transition: all 0.3s;"
            onmouseover="this.style.borderColor='rgba(0,212,255,0.4)';this.style.transform='translateY(-4px)'"
            onmouseout="this.style.borderColor='rgba(58,58,92,0.6)';this.style.transform='translateY(0)'"
          >
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
              <div style="width: 3rem; height: 3rem; border-radius: 0.75rem; background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(124,58,237,0.2)); display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                {{ platform.icon }}
              </div>
              <div>
                <h3 style="font-size: 1.125rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem;">{{ platform.name }}</h3>
                <span :style="{ color: platform.status === 'full' ? '#10b981' : (platform.status === 'partial' ? '#f59e0b' : '#ef4444'), fontSize: '0.8rem' }">
                  {{ platform.statusText }}
                </span>
              </div>
            </div>
            <p style="color: #9ca3af; font-size: 0.875rem; line-height: 1.6;">{{ platform.description }}</p>
            <div v-if="platform.features.length" style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
              <span
                v-for="feature in platform.features"
                :key="feature"
                style="padding: 0.25rem 0.75rem; background: rgba(0,212,255,0.1); border-radius: 9999px; font-size: 0.75rem; color: #00d4ff;"
              >
                {{ feature }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Supported Format Info -->
      <section style="padding: 2rem 0 3rem;">
        <div style="background: linear-gradient(135deg, rgba(30,30,63,0.6) 0%, rgba(15,15,35,0.8) 100%); border-radius: 1rem; border: 1px solid rgba(58,58,92,0.6); padding: 2rem;">
          <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; color: #fff;">支持的视频格式</h2>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem;">
            <div v-for="fmt in formats" :key="fmt.name" style="text-align: center; padding: 1rem; background: rgba(15,15,35,0.6); border-radius: 0.5rem;">
              <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{{ fmt.icon }}</div>
              <div style="color: #fff; font-weight: 600; font-size: 0.9rem;">{{ fmt.name }}</div>
              <div style="color: #9ca3af; font-size: 0.75rem;">{{ fmt.ext }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Quality Info -->
      <section style="padding: 0 0 4rem;">
        <div style="background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(0,212,255,0.1) 100%); border-radius: 1rem; border: 1px solid rgba(0,212,255,0.2); padding: 2rem; text-align: center;">
          <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: #fff;">支持多种清晰度</h2>
          <p style="color: #9ca3af; margin-bottom: 1.5rem;">从 360P 到 8K 超清，会员可享最高画质</p>
          <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div v-for="q in qualities" :key="q.name">
              <div style="font-size: 1.5rem; font-weight: 700; color: #00d4ff;">{{ q.value }}</div>
              <div style="color: #9ca3af; font-size: 0.8rem;">{{ q.name }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'

const platforms = [
  {
    name: 'YouTube',
    icon: '📺',
    status: 'full',
    statusText: '完全支持',
    description: '全球最大视频平台，支持所有视频格式下载，4K/8K超清可选',
    features: ['4K/8K超清', '字幕提取', 'Playlist下载']
  },
  {
    name: 'Bilibili (B站)',
    icon: '📱',
    status: 'full',
    statusText: '完全支持',
    description: '国内知名弹幕视频平台，支持大会员画质，批量下载',
    features: ['弹幕下载', '4K画质', '分P下载']
  },
  {
    name: '抖音',
    icon: '🎵',
    status: 'full',
    statusText: '完全支持',
    description: '短视频平台，智能去水印，支持图文和视频下载',
    features: ['自动去水印', '无水印下载', '批量下载']
  },
  {
    name: 'TikTok',
    icon: '🎶',
    status: 'partial',
    statusText: '部分支持',
    description: '国际版抖音，部分视频需要登录cookies才能下载',
    features: ['去水印', '需要Cookies']
  },
  {
    name: 'Twitter/X',
    icon: '🐦',
    status: 'full',
    statusText: '完全支持',
    description: '社交媒体平台，支持图片和视频下载',
    features: ['图片下载', '视频下载', 'GIF下载']
  },
  {
    name: 'Instagram',
    icon: '📷',
    status: 'partial',
    statusText: '部分支持',
    description: '图片社交平台，部分内容需要登录才能下载',
    features: ['图片下载', 'Stories支持']
  },
  {
    name: '微博',
    icon: '🔥',
    status: 'full',
    statusText: '完全支持',
    description: '中文社交媒体平台，支持视频和图片下载',
    features: ['视频下载', '图片下载', '长图下载']
  },
  {
    name: '快手',
    icon: '🎬',
    status: 'full',
    statusText: '完全支持',
    description: '短视频平台，支持去水印下载',
    features: ['自动去水印', '批量下载', '直播下载']
  },
  {
    name: '小红书',
    icon: '📕',
    status: 'full',
    statusText: '完全支持',
    description: '生活方式平台，支持图文和视频下载',
    features: ['图文下载', '视频下载', '去水印']
  }
]

const formats = [
  { name: 'MP4', icon: '🎬', ext: '视频格式' },
  { name: 'MKV', icon: '📦', ext: '高清封装' },
  { name: 'WEBM', icon: '🌐', ext: 'Web格式' },
  { name: 'MP3', icon: '🎵', ext: '音频提取' },
  { name: 'AAC', icon: '🔊', ext: '音频格式' }
]

const qualities = [
  { name: '360P', value: '360P' },
  { name: '480P', value: '480P' },
  { name: '720P', value: '720P' },
  { name: '1080P', value: '1080P' },
  { name: '4K', value: '4K' },
  { name: '8K', value: '8K' }
]
</script>