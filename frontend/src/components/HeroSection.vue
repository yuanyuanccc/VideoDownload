<template>
  <section style="padding: 4rem 0 3rem; text-align: center; position: relative; overflow: hidden;">
    <!-- 背景装饰 -->
    <div style="position: absolute; top: -50%; left: -10%; width: 40%; height: 200%; background: radial-gradient(circle, rgba(0,212,255,0.15) 0%, transparent 70%); pointer-events: none;"></div>
    <div style="position: absolute; top: -30%; right: -10%; width: 35%; height: 180%; background: radial-gradient(circle, rgba(124,58,237,0.15) 0%, transparent 70%); pointer-events: none;"></div>
    
    <div style="position: relative; z-index: 1;">
      <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.375rem 1rem; background: rgba(0,212,255,0.1); border-radius: 9999px; margin-bottom: 1.5rem; border: 1px solid rgba(0,212,255,0.2);">
        <span style="width: 6px; height: 6px; background: #00d4ff; border-radius: 50%; animation: pulse 2s infinite;"></span>
        <span style="color: #00d4ff; font-size: 0.75rem; font-weight: 500;">支持 1800+ 平台</span>
      </div>
      
      <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 0.75rem; letter-spacing: -0.025em;">
        <span style="background: linear-gradient(135deg, #fff 0%, #00d4ff 50%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
          万能视频下载器
        </span>
      </h1>
      <p style="color: #9ca3af; font-size: 1.125rem; margin-bottom: 2.5rem; max-width: 500px; margin-left: auto; margin-right: auto;">
        粘贴链接，一键解析，高速下载，支持 YouTube、B站、抖音等主流平台
      </p>
      
      <div style="max-width: 42rem; margin: 0 auto;">
        <div style="display: flex; gap: 0.5rem; padding: 0.5rem; background: #1e1e3f; border-radius: 1rem; border: 1px solid #3a3a5c; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);">
          <input
            v-model="url"
            type="text"
            placeholder="请粘贴视频链接..."
            style="flex: 1; padding: 1rem 1.25rem; background: transparent; color: #fff; border: none; outline: none; font-size: 1rem;"
            @keyup.enter="parseVideo"
          />
          <button
            @click="parseVideo"
            :disabled="loading || !url"
            style="padding: 1rem 2rem; background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%); color: white; font-weight: 700; border-radius: 0.75rem; border: none; cursor: pointer; font-size: 1rem; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 15px -3px rgba(0,212,255,0.4);"
            @mouseover="$event.target.style.transform='scale(1.02)'"
            @mouseout="$event.target.style.transform='scale(1)'"
          >
            <span v-if="loading" style="display: flex; align-items: center; gap: 0.5rem;">
              <svg style="width: 1.25rem; height: 1.25rem; animation: spin 1s linear infinite;" fill="none" viewBox="0 0 24 24">
                <circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              解析中
            </span>
            <span v-else>开始解析</span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['parsed'])
const url = ref('')
const loading = ref(false)

const parseVideo = async () => {
  if (!url.value) return
  
  let videoUrl = url.value.trim()
  
  if (videoUrl.includes('douyin.com')) {
    const modalMatch = videoUrl.match(/modal_id[=/](\d+)/)
    if (modalMatch) {
      videoUrl = `https://www.douyin.com/video/${modalMatch[1]}`
    }
    const avMatch = videoUrl.match(/av(\d+)/)
    if (avMatch) {
      videoUrl = `https://www.douyin.com/video/${avMatch[1]}`
    }
  }
  
  loading.value = true
  try {
    const response = await axios.post('/api/parse', { url: url.value })
    if (response.data.code === 0) {
      emit('parsed', response.data.data)
    } else {
      alert('解析失败，请检查链接是否正确')
    }
  } catch (error) {
    console.error('Parse error:', error)
    let msg = '解析失败，请检查链接是否正确'
    if (error.response?.data?.detail) {
      msg = error.response.data.detail
    } else if (error.message) {
      msg = error.message
    }
    if (msg.includes('cookies')) {
      msg = '该平台需要登录 cookies，暂不支持解析'
    }
    if (msg.includes('empty') || msg.includes('无内容')) {
      msg = '抖音解析失败，可能是网络或地区限制，请尝试其他平台（如B站、YouTube）'
    }
    if (msg.includes('Connection') || msg.includes('network') || msg.includes('Network')) {
      msg = '网络连接失败，请检查网络或代理设置'
    }
    if (msg.includes('Failed to establish')) {
      msg = '无法连接到服务器，请检查网络/代理'
    }
    console.log('Error message:', msg)
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>